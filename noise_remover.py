from bs4 import BeautifulSoup
import urllib.request
import nltk
from nltk.tokenize.stanford_segmenter import StanfordSegmenter
from langdetect import detect
import jieba.posseg as pseg
import jieba

class NoiseRemover:
    def __init__(self):
        self.prefix_tags = [0]

    def remove_noise(self, url, lang):
        fp = urllib.request.urlopen(url)
        mybytes = fp.read()

        tech_crunch_html = mybytes.decode("utf8")
        fp.close()

        soup = BeautifulSoup(tech_crunch_html, "html.parser")

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
        body_tokens = nltk.tokenize.word_tokenize(str(body))
        # print(body_tokens)

        body_tokens_clean = self.customize_tokenizer(body_tokens)
        # print(body_tokens_clean)

        # If chinese, extra tokenize step
        if lang == "chinese":
            body_tokens_clean = self.chinese_tokenize(body_tokens_clean)
            print(body_tokens_clean)

        self.prefix_sum_tags(body_tokens_clean)

        i, j = self.noise_remove(body_tokens_clean)
        print("i: " + str(i))
        print("j: " + str(j))
        # print(body_tokens_clean[i : j + 1])
        self.store_tokens_to_html(body_tokens_clean[i : j + 1])

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
        output_html_string = ""
        for token in tokens:
            output_html_string += token + "\n"
        # store clean tokens into html file
        html_file = open("tmp.html", "wb")
        html_file.write(output_html_string.encode("utf-8"))
        html_file.close()