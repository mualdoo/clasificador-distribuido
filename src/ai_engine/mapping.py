# src/ai_engine/mapping.py

CAT_MAP = {
    'cs': {
        'name': 'Computer Science',
        'subs': {
            'AI': 'Artificial Intelligence',
            'LG': 'Machine Learning',
            'NI': 'Networking',
            'CV': 'Computer Vision'
        }
    },
    'math': {
        'name': 'Mathematics',
        'subs': {
            'CO': 'Combinatorics',
            'ST': 'Statistics'
        }
    },
    'physics': {
        'name': 'Physics',
        'subs': {
            'gen-ph': 'General Physics',
            'quant-ph': 'Quantum Physics'
        }
    }
}

def get_levels(raw_tag):
    """Convierte 'cs.AI' en ('Computer Science', 'Artificial Intelligence')"""
    parts = raw_tag.split('.')
    main_code = parts[0]
    sub_code = parts[1] if len(parts) > 1 else 'General'
    
    main_info = CAT_MAP.get(main_code, {'name': main_code, 'subs': {}})
    main_name = main_info['name']
    sub_name = main_info['subs'].get(sub_code, sub_code)
    
    return main_name, sub_name