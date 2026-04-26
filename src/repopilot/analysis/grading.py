from repopilot.analysis.schemas import AnalysisResult, GradeResult

_MATURITY = [
    (1.5, "L1", "Prototype", "原型级"),
    (2.5, "L2", "Basic", "基础级"),
    (3.5, "L3", "Standard", "标准级"),
    (4.5, "L4", "Production", "生产级"),
    (5.1, "L5", "Enterprise", "企业级"),
]

_DIFFICULTY = [
    (1.5, "D1", "Beginner", "入门级"),
    (2.5, "D2", "Junior", "进阶级"),
    (3.5, "D3", "Intermediate", "实战级"),
    (4.5, "D4", "Senior", "资深级"),
    (5.1, "D5", "Expert", "专家级"),
]


def _map(score: float, table: list) -> tuple[str, str]:
    for threshold, level, en, zh in table:
        if score < threshold:
            return level, f"{level} {en}/{zh}"
    return table[-1][1], f"{table[-1][1]} {table[-1][2]}/{table[-1][3]}"


def grade(result: AnalysisResult) -> GradeResult:
    m_level, m_name = _map(result.maturity_score, _MATURITY)
    d_level, d_name = _map(result.difficulty_score, _DIFFICULTY)
    return GradeResult(
        maturity_level=m_level,
        maturity_name=m_name,
        difficulty_level=d_level,
        difficulty_name=d_name,
    )
