from pathlib import Path
from exceptions.validator_error import IncorrectInputName, IncorrectData, DataBaseValidatorError

class InputValidator:
    def __init__(self):
        self.word = self._profanity_words()

    def _profanity_words(self) -> set[str]:
        dir_path = Path(__file__).parent.resolve()
        data_ru = dir_path / "data" / "ru.txt"
        data_en = dir_path / "data"  / "en.txt"

        if not data_ru.exists():
            raise DataBaseValidatorError("ru.txt")
        if not data_en.exists():
            raise DataBaseValidatorError("en.txt")
            
        set_words = set()        
        with open(data_ru, "r", encoding="utf-8") as f:
            set_words.update([row.strip().lower() for row in f.readlines()]) 
        with open(data_en, "r", encoding="utf-8") as f:
            set_words.update([row.strip().lower() for row in f.readlines()])
        
        return set_words

    def validate_name_plyers(self, name_p1: str, name_p2: str) -> None:
        if name_p1.lower() == name_p2.lower():
            raise IncorrectInputName("Никнейм игроков не должны быть одинаковыми")
        self._validate_name(name_p1)
        self._validate_name(name_p2)
    
    def _validate_name(self, name: str) -> None:
        if not name:
            raise IncorrectData()
        if not all(row.isalpha() for row in name.split()):
            raise IncorrectInputName("Никнейм должнен состоять из букв")
        if self._validate_profanity_words(name):
            raise IncorrectInputName(f"Введенное слово в 'name': ({name}) является нецензурным")

    def _validate_profanity_words(self, text: str) -> bool:
        return any(row in text.lower() for row in self.word)