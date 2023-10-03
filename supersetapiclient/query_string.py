class QueryStringFilter:
    def __init__(self):
        self._filters = []

    def add(self, coluna:str, operador:str, valor):
        self._filters.append({
            'col':coluna,
            'opr':operador,
            'value':valor
        })

    @property
    def filters(self) -> dict:
        return self._filters