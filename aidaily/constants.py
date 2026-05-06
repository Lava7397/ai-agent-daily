"""Section layout and caps (single source for daily_data shape)."""

SECTION_META = {
    "research": {"icon": "🤖", "title_zh": "AI Agent 研究", "title_en": "Research"},
    "github": {"icon": "⭐", "title_zh": "GitHub 热门项目", "title_en": "GitHub Trending"},
    "models": {"icon": "🚀", "title_zh": "模型与行业动态", "title_en": "Models & Industry"},
    "community": {"icon": "🔥", "title_zh": "社区热议", "title_en": "Community"},
}

SECTION_KEYS: tuple[str, ...] = ("research", "github", "models", "community")
DEFAULT_MAX_SITE_ITEMS = 80

SECTION_KEY_TO_INDEX = {k: i for i, k in enumerate(SECTION_KEYS)}
