"""Run from repository root: py -3 -m backend.rag.demo"""
import json

from .api import load_store, retrieve_payload


def main():
    result = retrieve_payload(load_store(), {
        'criterion': {
            'id': 'custom_data_residency',
            'name': 'EU data residency',
            'evaluation_question': 'Are production records and backups stored in EU regions?',
        },
        'proposal_context': 'Production records and all backups remain in EU regions.',
        'requirement_context': 'Provide a named-region data-flow diagram and restoration demonstration.',
        'relevance_threshold': 2,
    })
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
