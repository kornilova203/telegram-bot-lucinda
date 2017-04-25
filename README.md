# Lucinda — telegram bot for learning new words
@englishVocabularyLucindaBot

[Описание на русском](https://github.com/kornilova-l/telegram-bot-lucinda#Идея)

## Idea
This bot will help to learn new English words.

User adds new words to personal dictionary (command /addwords), then he starts process of learning (command /startlearning)

It happens a lot when you learn a new word and forget it. Therefore I decided to implement application which in process of learning shows not only a word but a sentence with this word, so user will always see a word in context

It will make it easier for a user to remember the word and make associations with other words, understand how to properly use this word.

![screen from Telegram Desktop](https://pp.vk.me/c636918/v636918518/45ea4/4pjUJ6LPM90.jpg)
## Commands
* `/start` - description of bot
* `/help` - what bot can do
* `/addwords` - add words to dictionary
* `/deletewords` - delete word from dictionary
* `/printdict` - print dictionary
* `/startlearning` - start learnign
* `/stop` - stop current command

## How does it work?
Bot is written in Python using framework [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI).

Code with comments in English can be found here [bot.py](https://github.com/kornilova-l/telegram-bot-lucinda/blob/master/bot.py)

### Where it gets sentences with words?
Sentences with words bot gets using [Twinword API](https://www.twinword.com/api/index.php)

### Adding words to dictionary. Command `/addwords`
Person types command `/addwords`, then sends new word to bot *evidence - доказательство*

1. Bot writes this word to person's dictionary (if this word is new)
2. Bot searches for any examples with this word in his database of examples
3. If he does not find any, he makes request to Twinword and get response in JSON format
4. Bot adds array of examples in database

  Here is an example of such array:
  
  `['The evidence belies your statement.', 
  "The evidence invalidates the man's statement.", 
  'Was there evidence in the record that the victim was promiscuous ', 
  "The bulk of the evidence for the arrest warrant was Lawrence's statement."]`

Examples of sentences are added to database only ones when person add a new word. It is needed to prevent making requests to Twinword each time when person types /startlearning.

### Learning words. Command `/startlearning`

1. Bot checks person's dictionary. If it is empty, he sends a message "your dictionary is empty"
2. Bot adds the person to list of people who now are learning words.
3. Bot chooses random word from dictionary and sends to person sentence with this word
4. Bot remembers this word. When person sends answer, bot gives right answer

## Идея
Этот телеграм бот поможет запомнить новые английские слова. 

Пользователь добавляет слова в свой словарь (команда /addwords), а затем включал процесс изучения (команда /startlearning)

Часто возникает проблема, что выученные слова быстро забываются. Поэтому вместо того, чтобы просто спрашивать у пользователся перевод английского слова, Lucinda присылает предложение с его использованием. 

Таким образом пользователь видит слово в контексте и ему проще его запомнить, проассоциировать с другими словами, понять особенности его использования. В дальнейшем, когда пользователь встретит выученное слово, ему будет легче его вспомнить.  

![Пример взаимодействия с ботом. Скриншот из Telegram Desktop](https://pp.vk.me/c636918/v636918518/45ea4/4pjUJ6LPM90.jpg)
## Команды
* `/start` - описание бота
* `/help` - что умеет бот
* `/addwords` - добавить слова в свой словарь
* `/deletewords` - удалить слова из своего словаря
* `/printdict` - посмотреть свой словарь
* `/startlearning` - начать учить слова
* `/stop` - прервать текущую команду

## Как он работает
Бот написан на Python с использованием библиотеки [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI).

Код программы с комментариями на английском языке находится в файле [bot.py](https://github.com/kornilova-l/telegram-bot-lucinda/blob/master/bot.py)

### Особенности
Для хранения словарей пользователей используется модуль *shelve*, который позволяет сохранять key — value пары в файл и обеспечивает взаимодействие с ними. Получается простая база данный, где key — это id пользователя, а value — его словарь.

Примеры предложений со словами, которые учит пользователь, бот получает используя [Twinword API](https://www.twinword.com/api/index.php)

### Добавление слов в словарь. Команда `/addwords`
Предположим, пользователь ввёл команду `/addwords`, а затем отправил боту слово *evidence - доказательство*

1. Бот записывает это слово в словарь пользователя
2. Бот проверяет, есть ли уже примеры со словом evidence в его базе примеров
3. Если примеров не обнаруживается, то он делает запрос к twinword с этим словом и получает ответ в формате json
4. Если запрос был корректный и в twinword есть примеры с этим словом, то бот записывает в базу примеров полученный список с предложениями, в которых есть слово evidence. 

  Пример такого списка:
  
  `['The evidence belies your statement.', 
  "The evidence invalidates the man's statement.", 
  'Was there evidence in the record that the victim was promiscuous ', 
  "The bulk of the evidence for the arrest warrant was Lawrence's statement."]`

Примеры предложений для слова добавляются в базу примеров 1 раз, когда пользователь добавляет слово в словарь. Это нужно для того, чтобы не делать запросы к twinword каждый раз, когда пользователь учит слова.

Стоит отметить, что база примеров общая для всех. Так как у разных пользователей в их словарях могут быть одинаковые слова.

### Процесс изучения слов. Команда `/startlearning`

1. Бот проверяет, есть ли у пользователя в словаре слова. Если слов нет, то отправляет сообщение "your dictionary is empty"
2. Бот добавляет пользователя в список пользователей, которые сейчас учат слова (это необходимо делать, потому что иначе невозможно определить к какой команде относится следующее сообщение пользователя /addwords /deletewords или /startlearning) 
3. Бот выбирает случайное слово из словаря, ищет предложение с этим словом в базе примеров и отправляет его (если примера со словом нет, то бот оправляет само слово)
4. Бот запоминает отправленное слово, чтобы потом проверить ответ пользователя.
