import re

def tokenize_string(input_string):
    """
    Tokenize a string by splitting it into words, whitespace, and punctuation marks.
    
    Args:
    input_string (str): The input string to be tokenized.
    
    Returns:
    list: A list of tokens extracted from the input string.
    """
    # Regular expression to match words, whitespace, and punctuation marks
    pattern = r'\w+|[^\w\s]'
    
    # Tokenize the input string using the regular expression pattern
    tokens = re.findall(pattern, input_string)
    
    return tokens


def main():
    # Example usage:
    input_string = "Hello, how are you today?"
    tokens = tokenize_string(input_string)
    print(len(tokens))

if __name__ == '__main__':
    main()