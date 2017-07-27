import re
import sqlite3

class MarkovChainer(object):
    def __init__(self, order, brainfile):

        self.brainfile = brainfile

        # order as defined in local_settings.py, default 2
        self.order = order

        # array of sentence beginnings of no. of words (order)
        # self.beginnings = []

        # dictionary that holds info in format {"word word": ["word","word","word"]}
        # this is used with beginning to do the chaining
        self.freq = {}

        # Connect to SQLite brain
        self.db = sqlite3.connect(brainfile)
        self.brain = self.db.cursor()

    #pass a string with a terminator to the function to add it to the markov lists.
    #this needs to be changed to stick text into the SQL database instead of the object
    def add_sentence(self, string, terminator):

        #initialise data by joining the string parameter given to it
        data = "".join(string)

        #create an array of words by splitting data into constituent words
        words = data.split()

        #initialise array "buf" that is used to hold words when creating key-word pairs
        buf = []

        # if there are more words than the order parameter (default 2)
        if len(words) > self.order:

            # append the terminator passed in by parameter to words array
            words.append(terminator)

            # append the first to orderth words (1st and 2nd by default)
            # to the array beginnings, which is used for sentence starts
            # for mining
            # self.beginnings.append(words[0:self.order])

            # Do the same for shoving into the SQL DB

            winkyword = ""

            for winky in words[0:self.order]:
                if winky != words[self.order]:
                    winkyword += winky + " "
                else:
                    winkyword += winky

            self.brain.execute("INSERT INTO beginnings VALUES (?)",(winkyword,))

        else:
            # if there aren't enough words then don't add a terminator or generate a begining
            # this is another possible source of Order 3+ not working - there aren't enough beginnings?
            pass
        
        for word in words:
            # append a word to buf
            buf.append(word)

            #if the length of buf is order + 1 i.e. there are order+1 words in it
            #the way this is currently coded, it will only work with order 2 because
            #mykey buf[-2] will be
            if len(buf) == self.order + 1:

            # set mykey to tuple of first and second words in buffer
            # (three words in buffer, 0 is word 1, -2 is word 2)
            # this needs to be recoded to remove the assumption that order is 2
            # if orders other than 2 are to work properly it needs to keep
            # adding stuff to a mykey list depending on order then flip it to a tuple if that's the only way
            # it can be used as a key.  Whatever!
            #    mykey = (buf[0], buf[-2])

                mykeysql = buf[0] + " " + buf[1]

            #if the key already exists, append the final word in the buffer to dictionary Freq
            #under the MyKey - ends up with an entry like {"hello there": ["I", "my", "sir"]}
            #SQL code would probably be to return all instances of KEY - VALUE and pick a random
            #returned row?

             #   if mykey in self.freq:
             #       self.freq[mykey].append(buf[-1])

                self.brain.execute("INSERT INTO markov VALUES (?,?)",(mykeysql,buf[-1]))

            #if there isn't a key in the dictionary equal to MyKey, create one and
            #add the value to the freq dictionary under mykey {"hello there": ["I"]}

            #   else:
            #       self.freq[mykey] = [buf[-1]]

            # remove the first word in the array ready to move onto the next

                buf.pop(0)

            else:
            # if buf isn't log enough to generate a key-word pair, load in another word
                continue

        #self.db.commit()
        return

    def add_text(self, text):

        #replace any special characters in text with full stops
        #mostly end of lines
        text = re.sub(r'\n\s*\n/m', ".", text)

        #defines separators for sentences
        seps = '([.!?;:])'

        #split text into pieces at each seperator
        #this gives an array of sentences and seperator chars
        pieces = re.split(seps, text)

        #initialise variable to hold a sentence
        sentence = ""

        # for each piece of text in pieces
        for piece in pieces:
            # if the piece isn't empty
            if piece != "":
                if re.search(seps, piece):
                # if the piece contains a seperator as defined above
                # then call add_sentence, using whatever is in sentence at the time
                # and the current piece which is a seperator
                # as the "terminator" passed into add_sentence
                    self.add_sentence(sentence, piece)
                #clear sentence ready to load next piece after adding to brain file
                    sentence = ""
                else:
                #if the piece is text and not a seperator then put it into sentence
                #this will have it ready to pass to add_sentence next time round the look
                    sentence = piece

    #Generate the goofy sentences that become your tweet.
    def generate_sentence(self):
        # set res to a random (order) number of words from beginnings list
        # res = random.choice(self.beginnings)

        sqlres = self.brain.execute("SELECT * FROM beginnings ORDER BY RANDOM() LIMIT 1").fetchone()
        res = sqlres[0].split()

        if len(res)==self.order:
        # if res is the same length as order then can
        # proceed generating another word

            #nw is "next word/new word"?
            nw = True

            # while nw isn't none - the loop below sets
            # nw to "None" when it calls next_word_for
            # and that doesn't come back with an answer
            # when that happenes it effectively ends
            # the sentence

            while nw != None:
                # This also needs recoding to remove assumption of order=2
                # if orders other than 2 are to be used

                #restup = res tuple and makes a tuple of last two words in res
                #so "hello there sir" becomes ("there", "sir")
                restup = res[-2] + " " + res[-1]
              #  print "restup: " + restup

                try:
                    # try to get next word using last two words of res
                    nw = self.next_word_for(restup)

                    # if next_word_for returned an actual word
                    # then append it to list res
                    if nw != None:
                        res.append(nw)

                    # if it came back empty, carry on, this will cause
                    # while loop to end because nw == None
                    else:
                        continue

                # if attempting to look up nw falls over for any reason
                # then try to do it again because nw != None still applies
                except:
                    nw = False

            # create list new_res using all words in res except last two
            new_res = res[0:-2]

            # if the first word in the array new_res is a title (following words are capitalised)
            # or if first word is upper case then do nothing, otherwise capitalise the first word

            if new_res[0].istitle() or new_res[0].isupper():
                pass
            else:
                new_res[0] = new_res[0].capitalize()

            #initialise a string variable for sentence
            sentence = ""

            # new_res has all but last two words in sentence
            # spool them all into a sentence by splitting up with spaces

            for word in new_res:
                sentence += word + " "

            # add last two words from res that weren't contained in new_res
            sentence += res[-2] + res[-1]

        else:
        # if res isn't the same length as order the whole thing doesn't work
        # so return a null value
            sentence = None

        return sentence

    def next_word_for(self, words):
        try:

            sqlarr = self.brain.execute("SELECT val FROM markov WHERE key=? ORDER BY RANDOM() LIMIT 1", (words,))

            # next word/s is/are a random choice of one of these words
            # next_words = random.choice(arr)
            next_words = sqlarr.fetchone()
            next_words = next_words[0]

            return next_words

        except:
            # if there's nothing in the database for the combination (words)
            # then return nothing, because there's nothing to do
            return None

    def init_db(self):

        # Clears out DB ready for use
        # Or creates tables in DB
        try:
            print "Clearing tables"
            self.brain.execute("DROP TABLE markov")
            self.brain.execute("DROP TABLE beginnings")

            print "Tables cleared in brain"
            self.brain.execute("CREATE TABLE markov(key, val)")
            self.brain.execute("CREATE TABLE beginnings(begin)")

            self.db.commit()

        except:
            print "New brain file, creating tables"
            self.brain.execute("CREATE TABLE markov(key, val)")
            self.brain.execute("CREATE TABLE beginnings(begin)")

            self.db.commit()

    def commit_db(self):
        self.db.commit()

    def compact_db(self):
        self.brain.execute("VACUUM")

    def duplicate_tweet(self, tweet):
         if self.brain.execute("SELECT * FROM tweets WHERE tweet=?",(tweet,)).fetchone():
            return True
         else:
            return False

if __name__ == "__main__":
    print "Try running ebooks.py first"
