def camel_case_split(s):
    # use map to add an underscore before each uppercase letter
    modified_string = list(map(lambda x: '_' + x if x.isupper() else x, s))
    # join the modified string and split it at the underscores
    split_string = ''.join(modified_string).split('_')
    # remove any empty strings from the list
    split_string = list(filter(lambda x: x != '', split_string))
    return " ".join(split_string)

str1 = "GeeksForGeeks"
print(camel_case_split(str1))
str2 = "ThisIsInCamelCase"
print(camel_case_split(str2))
#This code is contributed by Edula Vinay Kumar Reddy
