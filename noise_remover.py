import re
from bs4 import BeautifulSoup
import urllib.request
import nltk
from langdetect import detect
import jieba.posseg as pseg
import jieba
import string
import codecs

class NoiseRemover:
    def __init__(self):
        self.prefix_tags = [0]

    def remove_noise(self, url, lang):
        '''fp = urllib.request.urlopen(url)
        mybytes = fp.read()

        tech_crunch_html = mybytes.decode("utf8")
        fp.close()'''

        html_text = self.get_html_from_file("./folder/en/techcrunch.com#2020#09#28#amazon-launches-a-4-99-per-month-personal-shopper-service-for-mens-fashion#.html")
        soup = BeautifulSoup(html_text, "html.parser")
        body = soup.find("body")

        # remove script
        for b in body.select("script"):
            b.extract()
        # remove image tags
        for b in body.select("img"):
            b.extract()
        for b in body.select("input"):
            b.extract()
        for b in body.select("a"):
            b.extract()
        for b in body.select("footer"):
            b.extract()

        body_string_quotes_cleaned = self.clean_quotes(str(body))

        body_tokens = nltk.tokenize.word_tokenize(body_string_quotes_cleaned)

        body_tokens_clean = self.customize_tokenizer(body_tokens)
        # print(body_tokens_clean)

        # If chinese, extra tokenize step
        if lang == "chinese":
            body_tokens_clean = self.chinese_tokenize(body_tokens_clean)

        self.prefix_sum_tags(body_tokens_clean)

        i, j = self.noise_remove(body_tokens_clean)
        # print("i: " + str(i))
        # print("j: " + str(j))
        # print(body_tokens_clean[i : j + 1])

        self.store_tokens_to_html(body_tokens_clean[i : j + 1])

    def get_html_from_file(self, file_path):
        with codecs.open(file_path, "r", "utf-8") as file:
            data = file.read()
        return data

    def customize_tokenizer(self, tokens):
        new_tokens = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if tokens[i] == '<':
                i += 1
                while tokens[i] != '>':
                    token += ' ' + tokens[i]
                    i += 1
                token += '>'
            i += 1
            new_tokens.append(token)
        return new_tokens

    def prefix_sum_tags(self, tokens):
        prefix_tags = [0]
        for token in tokens:
            if '<' in token:
                prefix_tags.append(prefix_tags[-1] + 1)
            else:
                prefix_tags.append(prefix_tags[-1])
        self.prefix_tags = prefix_tags

    def noise_remove(self, tokens):
        prefix_tags = self.prefix_tags
        maxi = maxj = -1
        max = 0

        for i in range(len(tokens) - 1):
            for j in range(i + 1, len(tokens)):
                sum = prefix_tags[i] + ((j - i + 1) - (prefix_tags[j + 1] - prefix_tags[i])) + (prefix_tags[-1] - prefix_tags[j + 1])
                if sum > max:
                    maxi = i
                    maxj = j
                    max = sum
        return (maxi, maxj)

    def get_text_only_tokens(self, tokens):
        new_tokens = []
        for token in tokens:
            if "<" not in token:
                new_tokens.append(token)
        return new_tokens

    def chinese_tokenize(self, tokens):
        for i in range(len(tokens)):
            try:
                lang = detect(tokens[i])
            except:
                lang = "zh-cn"
            if lang == "zh-cn":
                words = pseg.cut(tokens[i])
                counter = i
                for word in words:
                    tokens.insert(counter, word.word)
                    counter += 1
                del tokens[counter]
        return tokens

    def store_tokens_to_html(self, tokens):
        # convert list to string
        new_line_checker = False

        output_html_string = ""
        for i in range(len(tokens)):
            token = tokens[i]
            if "<" in token and ">" in token:
                if new_line_checker == False:
                    output_html_string += "\n"
                    new_line_checker = True
            else:
                output_html_string += token
                if i+1 < len(tokens):
                    next_token = tokens[i+1]
                    if any(character in string.punctuation for character in next_token):
                        if len(next_token) > 2:
                            output_html_string += " "
                    else:
                        output_html_string += " "

                new_line_checker = False

        # store clean tokens into html file
        html_file = open("tmp.txt", "wb")
        reverted_text = self.revert_double_quotes(output_html_string)
        html_file.write(reverted_text.encode("utf-8"))
        html_file.close()

    def clean_quotes(self, text):
        left_single_quote = "‘"
        right_single_quote = "’"
        left_double_quote = "“"
        right_double_quote = "”"
        text = text.replace(left_single_quote, "'")
        text = text.replace(right_single_quote, "'")
        text = text.replace(left_double_quote, "((")
        text = text.replace(right_double_quote, "))")
        '''for i, token in enumerate(tokens):
            if left_single_quote in token:
                tokens[i] = token.replace(left_single_quote, "'")
            elif right_single_quote in token:
                tokens[i] = token.replace(right_single_quote, "'")
            elif left_double_quote in token:
                tokens[i] = token.replace(left_double_quote, '"')
            elif right_double_quote in token:
                tokens[i] = token.replace(right_double_quote, '"')'''

        return text

    def revert_double_quotes(self, text):
        text = text.replace("(( ", " \"")
        text = text.replace("))", "\"")
        return text