from bs4 import BeautifulSoup, Comment
import urllib.request
import re
import tokenize
import nltk
from nltk import word_tokenize
import lxml

# customize tokenizer
def customize_tokenizer(tokens):
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

# calculate tag counts in a token list
def calculate_tag(tokens):
    tag_count = 0
    for token in tokens:
        if "<" in token:
            tag_count += 1
    return tag_count

def noise_remove(tokens):
    maxi = maxj = -1
    max = 0
    for i in range(len(tokens) - 1):
        for j in range(i + 1, len(tokens)):
            left = tokens[:i]
            mid = tokens[i:j + 1]
            right = tokens[j + 1:]
            sum = calculate_tag(left) + (len(mid) - calculate_tag(mid)) + calculate_tag(right)
            if sum > max:
                maxi = i
                maxj = j
                max = sum
    return (maxi, maxj)

def get_text_only_tokens(tokens):
    new_tokens = []
    for token in tokens:
        if "<" not in token:
            new_tokens.append(token)
    return new_tokens

fp = urllib.request.urlopen("https://techcrunch.com/2020/09/25/postmates-cuts-losses-in-q2-as-it-heads-towards-tie-up-with-uber/")
mybytes = fp.read()

tech_crunch_html = mybytes.decode("utf8")
fp.close()

soup = BeautifulSoup(tech_crunch_html, "html.parser")

body = soup.find("body")

# remove script
for b in body.select("script"):
    b.extract()

body_tokens = nltk.tokenize.word_tokenize(str(body))
print(body_tokens)

body_tokens_clean = customize_tokenizer(body_tokens)

print(body_tokens_clean)

'''i = 15
j = 1671'''

i, j = noise_remove(body_tokens_clean)
print("i: " + str(i))
print("j: " + str(j))

body_tokens_clean_noise_removed = get_text_only_tokens(body_tokens_clean[i:j+1])
print(body_tokens_clean_noise_removed)
print(len(body_tokens_clean_noise_removed))