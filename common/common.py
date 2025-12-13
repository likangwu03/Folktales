from typing import Any

def pad_or_truncate(lst: list, length: int, pad_value: Any = None):
	if len(lst) < length:
		return lst + [pad_value] * (length - len(lst))
	else:
		return lst[:length]