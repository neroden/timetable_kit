from __future__ import annotations

from timetable_kit.debug import debug_print


def span(class_name: str = "") -> str:
    """Returns a span tag with the class specified or a closing tag if blank"""
    return f'<span class="{class_name}">' if class_name else "</span>"


def span_enclose(span_class: str = "", *text: str) -> str:
    """Returns the text provided surrounded in a span tag with the specified tag.
    If multiple pieces of text are provided, they are stitched together before being surrounded in the tag.
    If no text is provided, the empty span tag is returned.
    If no class is provided, the stitched together text is returned.
    If you call this with no arguments, you will get a blank string. What are you doing?
    """
    if span_class:
        return f"{span(span_class)}{''.join(text)}{span()}"
    else:
        return "".join(text)


def recurse_update_dict(default: dict, update: dict) -> dict:
    for key, value in default.items():
        if isinstance(value, dict):
            if key in update:
                update_val = update[key]
                if isinstance(update_val, dict):
                    recurse_update_dict(value, update_val)
                else:
                    default[key] = update_val
        else:
            default[key] = update.get(key, value)
    return default


def test():
    assert span() == "</span>"
    assert span("classy") == '<span class="classy">'
    assert span_enclose("classy") == '<span class="classy"></span>'
    assert span_enclose("classy", "hi there") == '<span class="classy">hi there</span>'
    assert (
        span_enclose("classy", "hi there", " it's testing time")
        == '<span class="classy">hi there it\'s testing time</span>'
    )
    assert span_enclose(
        "both",
        span_enclose("first", "stuff"),
        span_enclose("second", "stuff"),
    ) == (
        '<span class="both">'
        '<span class="first">stuff</span>'
        '<span class="second">stuff</span>'
        "</span>"
    )


if __name__ == "__main__":
    test()
    debug_print(0, "Tests passed!")
