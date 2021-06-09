from dataclasses import dataclass, field


@dataclass()
class TableData:
    @dataclass()
    class _Row:
        values: list[str] = field(default_factory=list)

    headers: list[str] = field(default_factory=list)
    rows: list[_Row] = field(default_factory=list)

    def addRow(self, vals):
        self.rows.append(self._Row(values=vals))
