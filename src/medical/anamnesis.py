from copy import deepcopy


GENERAL_FIELDS = {
    "main_complaint": "Что вас беспокоит?",
    "duration": "Как давно это началось?",
    "severity": "Оцените выраженность симптома от 0 до 10.",
    "temperature": "Есть ли температура?",
    "allergies": "Есть ли у вас аллергии?",
    "medications": "Принимаете ли вы сейчас какие-либо лекарства?",
    "chronic_diseases": "Есть ли у вас хронические заболевания?",
}

ABDOMINAL_FIELDS = {
    "pain_location": "Где именно болит живот?",
    "pain_character": "Какая боль: острая, тупая, схваткообразная или жгучая?",
    "nausea": "Есть ли тошнота?",
    "vomiting": "Была ли рвота?",
    "stool": "Есть ли диарея или запор?",
    "movement_pain": "Усиливается ли боль при движении?",
    "appetite": "Изменился ли аппетит?",
}


class AnamnesisManager:
    def __init__(self):
        self.fields = deepcopy(GENERAL_FIELDS)
        self.answers = {}
        self.specialty_added = False

    def _detect_specialty(self):
        text = " ".join(str(v).lower() for v in self.answers.values())

        print("ANAMNESIS TEXT =", text)

        if not self.specialty_added and any(
            word in text for word in ["живот", "брюш", "бок"]
        ):
            print("ADDING ABDOMINAL FIELDS")
            self.fields.update(deepcopy(ABDOMINAL_FIELDS))
            self.specialty_added = True

    def update(self, extracted: dict):
        empty_values = {
            None,
            "",
            "none",
            "null",
            "not specified",
            "not provided",
            "unknown",
            "не указано",
            "неизвестно",
            "нет данных",
        }

        for key, value in extracted.items():
            if value is None:
                continue

            normalized = str(value).strip().lower()

            if normalized in empty_values:
                continue

            self.answers[key] = value

        self._detect_specialty()

    def get_next_question(self) -> str:
        self._detect_specialty()

        for key, question in self.fields.items():
            if key not in self.answers:
                return question
            
        print("FIELDS =", list(self.fields.keys()))
        print("ANSWERS =", self.answers)

        return "Спасибо. Анамнез собран."
    
    def get_next_field(self):
        self._detect_specialty()

        for key in self.fields.keys():
            if key not in self.answers:
                return key

        return None
    
    def get_missing_fields(self):
        self._detect_specialty()

        return {
            key: question
            for key, question in self.fields.items()
            if key not in self.answers
        }

    def to_dict(self) -> dict:
        return self.answers