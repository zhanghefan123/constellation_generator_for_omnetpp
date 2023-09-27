import prompt_toolkit.validation as validation


class IntegerValidator(validation.Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise validation.ValidationError(message="Please enter a number", cursor_position=len(document.text))


class FloatValidator(validation.Validator):
    def validate(self, document):
        try:
            float(document.text)
        except ValueError:
            raise validation.ValidationError(message="Please enter a number", cursor_position=len(document.text))