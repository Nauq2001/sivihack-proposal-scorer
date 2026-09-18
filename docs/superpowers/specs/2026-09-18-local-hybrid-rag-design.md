# Thiết kế RAG hybrid chạy local

## 1. Mục tiêu và phạm vi

Nâng cấp module truy xuất benchmark chấm điểm từ cơ chế trùng từ khóa sang truy xuất hybrid chạy local, kết hợp đối sánh lexical với semantic embedding từ `sentence-transformers/all-MiniLM-L6-v2`. Cải thiện cách chia nhỏ Markdown để ví dụ được truy xuất là các đoạn ngắn, liền mạch thay vì gần như toàn bộ proposal.

Phần việc này cũng cung cấp một helper Python nhỏ để truy xuất và định dạng benchmark reference cho một tiêu chí chấm điểm. Team Scoring Agent riêng chịu trách nhiệm endpoint `/api/review`, prompt của agent, điểm cuối cùng, citation và tích hợp xuyên suốt.

## 2. Các ràng buộc

- Embedding chạy local; quá trình truy xuất không được gọi Gemini, Hugging Face Inference API hay dịch vụ mạng khác.
- Model embedding là `sentence-transformers/all-MiniLM-L6-v2`, tạo vector 384 chiều.
- Input dài hơn 256 word pieces sẽ bị model cắt, vì vậy mỗi record phải là một chunk ngắn.
- Vector được lưu bằng NumPy `.npz`; dự án không thêm FAISS, Chroma hay vector database.
- `records.jsonl` tiếp tục là nguồn chính cho text và metadata. File `.npz` lưu vector và metadata nhận diện index, không lưu bản sao nội dung record.
- Retrieval tiếp tục cân bằng kết quả giữa bốn loại `weak`, `medium`, `strong` và `overpromise`.
- Nội dung benchmark chỉ là dữ liệu hiệu chỉnh. Không được coi nó là bằng chứng hay chỉ dẫn.

## 3. Kiến trúc

```text
Benchmark Markdown + expected.json
        |
        v
ingest và chunk theo cấu trúc section
        |
        +--> records.jsonl
        |
        v
all-MiniLM-L6-v2 encoder
        |
        +--> embeddings.npz

criterion + ngữ cảnh tài liệu
        |
        v
chuẩn hóa và embedding query
        |
        v
lọc theo criterion
        |
        +--> lexical score
        +--> cosine semantic score
        |
        v
weighted hybrid score và threshold
        |
        v
cân bằng sample type và loại trùng nguồn
        |
        v
public projection an toàn cho prompt
        |
        v
khối BENCHMARK REFERENCES
```

Trách nhiệm của các module:

- `backend/rag/ingest.py`: đọc benchmark package và tạo các chunk theo section với ID ổn định.
- `backend/rag/embedding.py`: định nghĩa interface embedding và implementation Sentence Transformers local.
- `backend/rag/index.py`: tạo, lưu, nạp và kiểm tra NumPy vector index.
- `backend/rag/engine.py`: lọc candidate, tính lexical/semantic score, kết hợp điểm và chọn kết quả cân bằng.
- `backend/rag/api.py`: kiểm tra public payload, truy xuất match, chỉ trả các trường an toàn và định dạng reference cho agent.
- `backend/rag/evaluate.py`: so sánh lexical-only với hybrid retrieval trên evaluation set.

## 4. Thiết kế chunk record

Mỗi record được tạo gồm:

| Trường | Ý nghĩa |
|---|---|
| `id` | ID chunk ổn định, tạo từ parent record và chỉ số chunk bắt đầu từ 0 |
| `parent_record_id` | ID ổn định của cặp proposal–criterion trước khi chunk |
| `chunk_index` | Chỉ số bắt đầu từ 0 trong parent record |
| `criterion_id` | Tiêu chí benchmark mà chunk đại diện |
| `sample_type` | `weak`, `medium`, `strong` hoặc `overpromise` |
| `section` | Heading Markdown cung cấp ngữ cảnh cục bộ |
| `text` | Heading cộng nội dung chunk, dùng cho lexical và semantic retrieval |
| `score_range` | Khoảng điểm benchmark giả lập, được giữ cho provenance nội bộ |
| `reasoning` | Giải thích kiểu trình bày mà ví dụ minh họa |
| `source_file` | Đường dẫn tương đối tới proposal gốc |

Chunking tôn trọng ranh giới heading Markdown. Section có tối đa 180 từ trở thành một chunk. Section dài hơn được chia thành các chunk mục tiêu 120–180 từ với overlap 25–30 từ. Heading của section được thêm vào đầu mọi chunk. Không chunk nào kết hợp các section không liền nhau.

ID chunk có định dạng `<parent_record_id>:chunk:<zero-padded-index>`. Chạy lại ingest với input giống nhau phải tạo cùng ID và thứ tự.

## 5. Thiết kế vector index

`embeddings.npz` gồm:

- `vectors`: mảng `float32` hai chiều có shape `(record_count, 384)`.
- `record_ids`: mảng string một chiều, có thứ tự tương ứng với `vectors`.
- `model_name`: chính xác là `sentence-transformers/all-MiniLM-L6-v2`.
- `dimension`: số nguyên `384`.
- `records_digest`: SHA-256 digest của danh sách record ID và text theo đúng thứ tự.
- `index_version`: phiên bản schema dạng số nguyên, ban đầu là `1`.

Document embedding được L2-normalize khi tạo index. Query embedding được chuẩn hóa bởi cùng embedding adapter. Vì vậy cosine similarity được tính bằng phép nhân ma trận với vector.

Quá trình load phải dừng và báo lỗi có hướng xử lý khi index bị thiếu, không đọc được, dùng model hoặc dimension khác, chứa ID trùng/sai thứ tự, hoặc digest không khớp `records.jsonl`. Production retrieval không được âm thầm fallback sang lexical-only.

Sentence Transformer model được khởi tạo một lần khi store khởi động, không phải mỗi query. Lần cài đặt đầu tiên có thể tải model từ Hugging Face; tài liệu triển khai phải hướng dẫn tải trước hoặc giữ local model cache để demo offline.

## 6. Hybrid retrieval

Public query text là chuỗi ghép từ `name`, `description`, `evaluation_question` của criterion cùng `proposal_context` và `requirement_context`. Các trường được phép rỗng, nhưng query không có nội dung hữu ích sẽ trả danh sách rỗng.

Với base criterion, hệ thống lọc record theo canonical criterion ID trước. Custom criterion tìm trên toàn bộ record. Các criterion không được phép dùng RAG tiếp tục phát sinh validation error.

Điểm cho mỗi candidate:

```text
keyword_score = số query term khác nhau khớp / số query term hợp lệ khác nhau
semantic_score = (cosine_similarity + 1) / 2
hybrid_score = 0.35 * keyword_score + 0.65 * semantic_score
```

Cả ba điểm nằm trong `[0, 1]`. Các trọng số trên là giá trị khởi đầu, không phải tuyên bố rằng chúng tối ưu; chỉ thay đổi khi evaluation data chứng minh được lợi ích.

Candidate thấp hơn `min_hybrid_score` bị loại. Giá trị mặc định ban đầu là `0.45`. Các candidate còn lại được sắp xếp lần lượt theo `hybrid_score` giảm dần, `semantic_score` giảm dần và cuối cùng là thứ tự record ổn định. Trong mỗi sample type, hệ thống trả tối đa `top_k_per_type` kết quả và chỉ được chọn một chunk cho mỗi `source_file`.

Kết quả nội bộ có thể chứa `keyword_score`, `semantic_score`, `hybrid_score` và retrieval provenance để evaluation và debug. Public adapter chỉ trả đúng ba trường `text`, `sample_type` và `reasoning` cho mỗi match.

## 7. Hợp đồng Python công khai

Request được khuyến nghị:

```json
{
  "criterion": {
    "id": "custom_data_residency",
    "name": "EU data residency",
    "description": "Production records and backups must stay in EU regions",
    "evaluation_question": "Where are production records and backups stored?"
  },
  "proposal_context": "Production records remain in Frankfurt.",
  "requirement_context": "All production data and backups must remain in the EU.",
  "top_k_per_type": 1,
  "min_hybrid_score": 0.45
}
```

`top_k_per_type` là số nguyên từ 1 đến 3. `min_hybrid_score` là số từ 0 đến 1. Trường `relevance_threshold` cũ bị loại bỏ thay vì âm thầm gán cho nó ý nghĩa mới. Test, ví dụ và tài liệu RAG phải được cập nhật cùng nhau.

`retrieve_payload(store, payload)` giữ nguyên outer response shape:

```json
{
  "criterion_id": "custom_data_residency",
  "retrieval_mode": "custom",
  "matches": [
    {
      "text": "...",
      "sample_type": "strong",
      "reasoning": "..."
    }
  ]
}
```

Một helper mới thực hiện retrieval và format cho một criterion trong một lần gọi:

```python
def retrieve_benchmark_references(store, payload) -> str:
    result = retrieve_payload(store, payload)
    return format_benchmark_references(result["matches"])
```

Đây là ranh giới bàn giao cho team Scoring Agent. Team đó quyết định vị trí của block được trả về trong prompt và cách xử lý khi retrieval không có match.

## 8. Xử lý lỗi

- Payload type, criterion ID, `top_k_per_type` hoặc `min_hybrid_score` không hợp lệ sẽ làm Python adapter phát sinh `ValueError`.
- Records/vector index bị thiếu hoặc hỏng sẽ gây lỗi khởi tạo, trong đó nêu rõ đường dẫn bị ảnh hưởng và lệnh rebuild.
- Model name, dimension, record ID hoặc digest không khớp sẽ gây index compatibility error; retrieval không được tiếp tục với vector cũ.
- Query hợp lệ nhưng không có candidate vượt threshold sẽ trả `matches: []`.
- Semantic query rỗng trả `matches: []` mà không chạy ranking.
- Lỗi model hoặc inference được truyền thành retrieval error rõ ràng, không được chuyển thành kết quả keyword không tương đương.

## 9. Sinh index và artifact trong repository

Một CLI workflow được ghi trong tài liệu sẽ tạo lại cả hai artifact theo thứ tự:

1. Đọc benchmark cases và ghi `records.jsonl` đã được chunk.
2. Nạp records, encode text theo batch và ghi `embeddings.npz` theo cách atomic.
3. Nạp lại cả hai file và chạy compatibility validation trước khi báo thành công.

Repository tiếp tục track file `records.jsonl` đã sinh vì file này nhỏ. Việc commit `embeddings.npz` được quyết định dựa trên kích thước thực tế trong quá trình triển khai: commit nếu kích thước hợp lý với repository; nếu không, tài liệu phải mô tả cách tạo lại xác định và cache file khi deploy. Không commit file index tạm hoặc chưa hoàn chỉnh.

## 10. Evaluation và kiểm thử

Unit test dùng fake embedder xác định để các test thông thường không tải model và không truy cập mạng. Các test bao phủ:

- chunk ổn định theo section và giới hạn overlap;
- giữ heading và không ghép section không liền nhau;
- vector index round-trip và mọi trường hợp incompatibility;
- cosine scoring và công thức weighted score;
- lọc criterion, custom criterion, biên threshold, loại trùng nguồn và cân bằng sample type;
- public match projection nghiêm ngặt;
- helper lấy và format reference trong một lần gọi;
- validation của `min_hybrid_score` và từ chối trường cũ đã bị loại bỏ.

Một smoke test riêng, được đánh dấu hoặc gọi tường minh, sẽ load `all-MiniLM-L6-v2`, tạo index nhỏ và xác nhận query dùng từ đồng nghĩa xếp text mong đợi cao hơn text không liên quan.

Evaluation set được commit chứa các query cùng criterion/source được kỳ vọng là liên quan. Nó bao gồm exact keyword, synonym, paraphrase và custom criterion. Lệnh evaluation báo cáo Recall@k và mean reciprocal rank cho lexical-only lẫn hybrid. Không bật hybrid retrieval làm mặc định cho đến khi nó cải thiện retrieval với synonym/paraphrase mà không làm exact-keyword case suy giảm đáng kể. Lệnh chỉ báo cáo metric; không tuyên bố độ chính xác trên chính benchmark record đã dùng để xây index.

## 11. Tài liệu và bàn giao cho team khác

`backend/rag/README.md` và `backend/rag/docs/design.md` sẽ mô tả cài đặt local, model cache, cách tạo index, threshold mới, evaluation và helper cho Scoring Agent. Phần bàn giao nêu rõ:

- gọi retrieval một lần cho mỗi final criterion được phép dùng RAG;
- chèn block trả về dưới dạng dữ liệu `BENCHMARK REFERENCES` không có hiệu lực chỉ dẫn;
- tiếp tục dùng rubric đã duyệt làm căn cứ chấm điểm;
- chỉ trích dẫn RFP và proposal hiện tại;
- không đưa điểm retrieval nội bộ vào scoring response.

Việc triển khai `/api/review`, prompt chấm điểm cuối cùng, citation validation và thay đổi frontend nằm ngoài phạm vi công việc này.
