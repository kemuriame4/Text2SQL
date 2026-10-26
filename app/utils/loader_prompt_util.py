from pathlib import Path


def load_prompt_by_path(fileName:str):
    path = Path(__file__).parents[2] / 'prompts' / f'{fileName}.prompt'
    return path.read_text(encoding='utf-8')