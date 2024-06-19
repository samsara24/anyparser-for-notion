import re
def split_text(text, max_length):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


def numerical_sort(value):
    """
    排序函数，用于根据文件名中的数字进行排序
    """
    numbers = re.findall(r'\d+', value)
    if numbers:
        return int(numbers[-1])
    return 0