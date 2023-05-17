def extract_text(text, start_string, end_string):
    start_index = text.find(start_string)
    end_index = text.find(end_string, start_index + len(start_string))
    if start_index == -1:
        return False
    if end_index == -1:
        return text[start_index + len(start_string):]
    return text[start_index + len(start_string):end_index]