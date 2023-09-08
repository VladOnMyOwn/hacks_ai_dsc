import re
from num2words import num2words
from pymorphy2 import MorphAnalyzer


REPLACE_DICT = {
    " упак ": " упаковка ",
    " дет ": " детский ",
    " бел ": " белый ",
    " цв ": " цветной ",
    " вс ": " высший сорт ",
    " фл ": " флаконы ",
    " жб ": " жестяная банка ",
    " жр ": " жевательная резинка ",
    " мал ": " маленький ",
    " изм арт ": " измерение артериального ",
    " зп ": " зубная паста ",
    " му ": " мягкая упаковка ",
    " туп ": " термоупаковка ",
    " морск ": " морской ",
    " хол ": " холодный ",
    " дкош ": " для кошек ",
    " шок ": " шоколад ",
    " для кош": " для кошек ",
    " нк ": " на кости ",
    " бу ": " без упаковки ",
    " хк ": " холодное копчение ",
    " син ": " синий ",
    " сини ": " синий ",
    " красн ": " красный ",
    " мкм ": " микрометр ",
    " микр ": " микрометр ",
    " перед ": " передний ",
    " ед ": " единица ",
    " рр ": " раствор ",
    " черн ": " черный ",
    " кл ": " класс ",
    " сух ": " сухой ",
    " вм ": " внутримышечно ",
    " ндс ": " добавленная стоимость ",
    " бзмж ": " без заменителя молочного жира ",
    " сзмж ": " с заменителем молочного жира ",
    " кг ": " килограмм ",
    " г ": " грамм ",
    " гр ": " грамм ",
    " мм ": " миллиметр ",
    " м ": " метр ",
    " шт ": " штука ",
    " мл ": " миллилитр ",
    " л ": " литр "
}
STOP_LIST = ['"', '\\', '/', '\r', '\n', '@', '%', '№', ':', "'", '&',
                    '!', '?', '[', ']', '(', ')', '<', '>',
                    ';', '|', '#', '`', '*', ',', '.', '_', '-', '=', '+',
                    '      ', '      ', '     ', '   ', '   ',
                    '   ', '  ', '  ', '  ', '  ',
                    ' это ',
                    ' как ',
                    ' так ',
                    ' и ',
                    ' в ',
                    ' над ',
                    ' к ',
                    ' до ',
                    ' на ',
                    ' но ',
                    ' за ',
                    ' то ',
                    ' с ',
                    ' ли ',
                    ' а ',
                    ' во ',
                    ' от ',
                    ' со ',
                    ' о ',
                    ' же ',
                    ' ну ',
                    ' вы ',
                    ' бы ',
                    ' что ',
                    ' кто ',
                    ' он ',
                    ' она ',
                    ' далее '
                    ]
a = 'a b c d e f g h i j k l m n o p q r s t u v w x y z ё'.split()
b = 'а в с д е ф г н и ж к л м н о р к р с т у в в х у з е'.split()
trans_dict = dict(zip(a, b))
TRANS_TABLE = ''.join(a).maketrans(trans_dict)
MIXED = re.compile(r'(\w*([а-я][a-z]|[a-z][а-я])\w*)')
MORPH = MorphAnalyzer()

def re_num2words(self, item_name):
    return re.sub(r"(\d+)", lambda x: f" {num2words(int(x.group(0)), lang='ru')} ", item_name)

def lemmatize(self, item_name):
    lemmatized = str()
    for word in list(item_name.split()):
        if self.MIXED.match(word):
            word = word.translate(self.TRANS_TABLE)

        if self.MORPH.word_is_known(word):
            lemmatized = fr'{lemmatized} {self.MORPH.parse(word)[0].normal_form}'
        else:
            lemmatized = fr'{lemmatized} {word}'

    return lemmatized.replace('ё', 'е').strip()

def normalize(self, item_name):
    #   "СокДобрый" -> "Сок Добрый"
    try:
        item_name = re.sub(r'([а-яa-z])([А-ЯA-Z])', r'\1 \2', item_name)
    except Exception as e:
        print(item_name)
        item_name = ""
        print(e)
    item_name = item_name.lower()
    item_name = item_name.strip()
    #   "1two" -> "1 two"
    item_name = re.sub(r'([0-9])([a-zа-я])', r'\1 \2', item_name)
    #   "one2" -> "one 2"
    item_name = re.sub(r'([a-zа-я])([0-9])', r'\1 \2', item_name)
    #   "ж/б ст/б" -> "жб стб"
    item_name = re.sub(r'\b([а-я]{1,2})[/-]([а-я]{1,2})\b', r'\1\2', item_name)
    #   "a b c d" -> "abcd"
    item_name = re.sub(r'(?<=(?<![а-яa-z])[а-яa-z]) (?=[а-яa-z](?![а-яa-z]))', '', item_name)
    #   "12345 words"->" words"
    item_name = re.sub(r'(\d{5,})', '', item_name)

    for r in self.STOP_LIST:
        item_name = item_name.replace(r, ' ')

    item_name = self._wrap_space(item_name)
    for r in self.REPLACE_DICT:
        item_name = item_name.replace(r, self.REPLACE_DICT[r])

    #   "    " -> " "
    item_name = re.sub(r'\s{2,}', ' ', item_name)
    item_name = self.lemmatize(item_name)
    item_name = self._wrap_space(item_name)
    return item_name

def wrap_space(self, item):
    return f" {item} "
