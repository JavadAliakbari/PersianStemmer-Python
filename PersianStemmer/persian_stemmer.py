'''
	File name: persian_stemmer.py
	Author: Hossein Taghi-Zadeh
	Date created: 25/09/2016
	Date last modified: 25/12/2016
'''
from PersianStemmer.stemming_rule import StemmingRule
from PersianStemmer.utils import Utils
from PersianStemmer.verb_stem import VerbStem

__author__ = 'Hossein Taghi-Zadeh'
__email__ = "h.t.azeri@gmail.com"

from patricia import trie
import re
import unicodedata
import os


class PersianStemmer(object):
    lexicon = trie()
    mokassarDic = trie()
    cache = trie()
    verbDic = trie()
    informalverbDic = trie()
    suffix_exception = trie()
    prefix_exception = trie()
    _ruleList = []
    verb_rule_list = []

    verbAffix = ["*ش", "*نده", "*ا", "*ار", "وا*", "اثر*",
                 "فرو*", "پیش*", "گرو*", "*ه", "*گار", "*ن"]
    suffix = ["كار", "ناك", "وار", "آسا", "آگین", "بار", "بان", "دان", "زار", "انه",
              "سار", "سان", "لاخ", "مند", "دار", "سازنده", "مرد", "گیرنده", "کننده", "گرا", "نما", "متر", "گان", ]
    prefix = ["بی", "با", "پیش", "غیر", "فرو", "هم", "نا", "یک"]
    prefixException = ["غیر"]
    suffixZamir = ["م", "ت", "ش"]
    suffixException = ["ها", "تر", "ترین", "ام", "ات", "اش"]
    suffix += suffixException

    PATTERN_FILE_NAME = os.path.dirname(__file__) + "/data/Patterns.fa"
    VERB_PATTERN_FILE_NAME = os.path.dirname(
        __file__) + "/data/verb_patterns.fa"
    VERB_FILE_NAME = os.path.dirname(__file__) + "/data/VerbList.fa"
    INFORMAL_VERB_FILE_NAME = os.path.dirname(
        __file__) + "/data/InformalVerbList.fa"
    DIC_FILE_NAME = os.path.dirname(__file__) + "/data/Dictionary.fa"
    SUFFIX_FILE_NAME = os.path.dirname(__file__) + "/data/suffix.fa"
    PREFIX_FILE_NAME = os.path.dirname(__file__) + "/data/prefix.fa"
    MOKASSAR_FILE_NAME = os.path.dirname(__file__) + "/data/Mokassar.fa"
    patternCount = 1
    enableCache = True
    enableVerb = True

    def __init__(self):
        try:
            self.loadRule()
            self.loadLexicon()
            self.load_suffix_exception()
            self.load_prefix_exception()
            self.loadMokassarDic()
            if self.enableVerb:
                self.loadVerbDic()
                self.loadInformalVerbDic()
                self.load_verb_rule()
        except Exception as ex:
            print(ex)

    def loadData(self, resourceName):
        result = []
        with open(resourceName, 'r', encoding="utf-8") as reader:
            result = [line.strip("\r\n ")
                      for line in reader if line.strip("\r\n ")]
        return result

    def loadVerbDic(self):
        if len(PersianStemmer.verbDic) > 0:
            return

        lines = self.loadData(PersianStemmer.VERB_FILE_NAME)
        for line in lines:
            arr = line.split("\t")
            PersianStemmer.verbDic[arr[0].strip()] = VerbStem(
                arr[1].strip(), arr[2].strip())

    def loadInformalVerbDic(self):
        if len(PersianStemmer.informalverbDic) > 0:
            return

        lines = self.loadData(PersianStemmer.INFORMAL_VERB_FILE_NAME)
        for line in lines:
            arr = line.split("\t")
            PersianStemmer.informalverbDic[arr[0].strip()] = VerbStem(
                arr[1].strip(), arr[2].strip())

    def str2bool(self, v):
        return v.lower() in ("yes", "true", "t", "1")

    def loadRule(self):
        if len(PersianStemmer._ruleList) > 0:
            return

        lines = self.loadData(PersianStemmer.PATTERN_FILE_NAME)
        for line in lines:
            arr = line.split(",")
            PersianStemmer._ruleList.append(StemmingRule(
                arr[0], arr[1], arr[2], int(arr[3]), self.str2bool(arr[4])))
        # PersianStemmer._ruleList = [StemmingRule(arr[0], arr[1], arr[2], int(arr[3]), self.str2bool(arr[4])) for line in lines for arr in line.split(",")]

    def load_verb_rule(self):
        if len(PersianStemmer.verb_rule_list) > 0:
            return

        lines = self.loadData(PersianStemmer.VERB_PATTERN_FILE_NAME)
        for line in lines:
            arr = line.split(",")
            PersianStemmer.verb_rule_list.append(StemmingRule(
                arr[0], arr[1], arr[2], int(arr[3]), self.str2bool(arr[4])))

    def loadLexicon(self):
        if len(PersianStemmer.lexicon) > 0:
            return

        lines = self.loadData(PersianStemmer.DIC_FILE_NAME)
        for line in lines:
            PersianStemmer.lexicon[line.strip("\r\n ")] = True

    def load_suffix_exception(self):
        if len(PersianStemmer.suffix_exception) > 0:
            return

        lines = self.loadData(PersianStemmer.SUFFIX_FILE_NAME)
        for line in lines:
            PersianStemmer.suffix_exception[line.strip("\r\n ")] = True

    def load_prefix_exception(self):
        if len(PersianStemmer.prefix_exception) > 0:
            return

        lines = self.loadData(PersianStemmer.PREFIX_FILE_NAME)
        for line in lines:
            PersianStemmer.prefix_exception[line.strip("\r\n ")] = True

    def loadMokassarDic(self):
        if len(PersianStemmer.mokassarDic) > 0:
            return

        lines = self.loadData(PersianStemmer.MOKASSAR_FILE_NAME)
        for line in lines:
            arr = line.split("\t")
            PersianStemmer.mokassarDic[arr[0].strip()] = arr[1].strip()

    def strip_accents(self, s):
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

    def normalization(self, s):
        newString = []
        for ch in s:
            if ch == 'ي':
                newString.append('ی')
            elif ch in ['ة', 'ۀ']:
                newString.append('ه')
            elif ch in ['‌', '‏']:
                newString.append(' ')
            elif ch == 'ك':
                newString.append('ک')
            elif ch == 'ؤ':
                newString.append('و')
            elif ch in ['إ', 'أ']:
                newString.append('ا')
            elif ch in ['\u064B',  # FATHATAN
                        '\u064C',  # DAMMATAN
                        '\u064D',  # KASRATAN
                        '\u064E',  # FATHA
                        '\u064F',  # DAMMA
                        '\u0650',  # KASRA
                        '\u0651',  # SHADDA
                        '\u0652']:  # SUKUN
                pass
            else:
                newString.append(ch)

        return ''.join(newString)

    def validation(self, sWord):
        return (sWord in PersianStemmer.lexicon or sWord in PersianStemmer.mokassarDic)

    def removeZamir(self, sInput, bState):
        sRule = "^(?P<stem>.+?)((?<=(ا|و))ی)?(ها)?(ی)?((ات)?( تان|تان| مان|مان| شان|شان)|ی|م|ت|ش|ء)$"
        if bState:
            sRule = "^(?P<stem>.+?)((?<=(ا|و))ی)?(ها)?(ی)?(ات|ی|م|ت|ش| تان|تان| مان|مان| شان|شان|ء)$"

        return self.extractStem(sInput, sRule)

    def getMokassarStem(self, sWord):

        if sWord in PersianStemmer.mokassarDic:
            return PersianStemmer.mokassarDic[sWord]
        else:
            sNewWord = self.removeZamir(sWord, True)
            if sNewWord in PersianStemmer.mokassarDic:
                return PersianStemmer.mokassarDic[sNewWord]
            else:
                sNewWord = self.removeZamir(sWord, False)
                if sNewWord in PersianStemmer.mokassarDic:
                    return PersianStemmer.mokassarDic[sNewWord]
        return ""

    def verbValidation(self, sWord):
        if sWord.find(' ') > -1:
            return ""

        j = 0
        for affix in PersianStemmer.verbAffix:
            if (j == 0 and (sWord[-1] == 'ا' or sWord[-1] == 'و')):
                sTemp = affix.replace("*", sWord + "ی")
            else:
                sTemp = affix.replace("*", sWord)

            if self.normalizeValidation(sTemp, True):
                return affix
            j = j + 1
        return ""

    def getPrefix(self, sWord):
        result = [
            sPrefix for sPrefix in PersianStemmer.prefix if sWord.startswith(sPrefix)]
        if len(result) > 0:
            return result[0]
        return ""

    def getPrefixException(self, sWord):
        result = [
            sPrefix for sPrefix in PersianStemmer.prefixException if sWord.startswith(sPrefix)]
        if len(result) > 0:
            return result[0]
        return ""

    def getSuffix(self, sWord):
        result = [
            sSuffix for sSuffix in PersianStemmer.suffix if sWord.endswith(sSuffix)]
        if len(result) > 0:
            return result[0]
        return ""

    def inRange(self, d, f, t):
        return d >= f and d <= t

    def normalizeValidation(self, sWord, bRemoveSpace):
        sWord = sWord.strip()
        l = len(sWord) - 2
        result = self.validation(sWord)

        if sWord.find('ا') == 0:
            sTemp = sWord.replace("ا", "آ", 1)
            result = self.validation(sTemp)
            if result:
                sWord = sTemp

        if self.inRange(sWord.find('ا'), 1, l):
            sTemp = sWord.replace('ا', 'أ')
            result = self.validation(sTemp)
            if result:
                sWord = sTemp

        if self.inRange(sWord.find('ا'), 1, l):
            sTemp = sWord.replace('ا', 'إ')
            result = self.validation(sTemp)
            if result:
                sWord = sTemp

        if self.inRange(sWord.find("ئو"), 1, l):
            sTemp = sWord.replace("ئو", "ؤ")
            result = self.validation(sTemp)
            if result:
                sWord = sTemp

        if sWord.endswith("ء"):
            sTemp = sWord.replace("ء", "")
            result = self.validation(sTemp)
            if result:
                sWord = sTemp

        if self.inRange(sWord.find("ئ"), 1, l):
            sTemp = sWord.replace("ئ", "ی")
            result = self.validation(sTemp)
            if result:
                sWord = sTemp

        if (bRemoveSpace):
            if self.inRange(sWord.find(' '), 1, l):
                sTemp = sWord.replace(" ", "")
                result = self.validation(sTemp)
                if result:
                    sWord = sTemp

        #	# دیندار
        #	# دین دار
        if sWord not in PersianStemmer.suffix_exception:
            sSuffix = self.getSuffix(sWord)
            if (sSuffix):
                # sTemp = sWord.replace(sSuffix, "")
                if sWord.endswith(" " + sSuffix):
                    sTemp = sWord.replace(" " + sSuffix, '')
                else:
                    sTemp = sWord.replace(sSuffix, '')
                result = self.validation(sTemp)
                if result:
                    sWord = sTemp

        if sWord not in PersianStemmer.prefix_exception:
            sPrefix = self.getPrefix(sWord)
            if sPrefix:
                if sWord.startswith(sPrefix + " "):
                    sTemp = sWord.replace(sPrefix + " ", '')
                else:
                    sTemp = sWord.replace(sPrefix, '')

                result = self.validation(sTemp)
                if result:
                    sWord = sTemp

        sPrefix = self.getPrefixException(sWord)
        if sPrefix:
            if (sWord.startswith(sPrefix + " ")):
                sTemp = sWord.replace(sPrefix + " ", "", 1)
            else:
                sTemp = sWord.replace(sPrefix, "", 1)

            result = self.validation(sTemp)
            if result:
                sWord = sTemp

        return sWord

    def isMatch(self, sInput, sRule):
        match = re.compile(sRule).search(sInput)
        if match:
            return True
        return False

    def extractStem(self, sInput, sRule, sReplacement="\g<stem>"):
        return re.sub(sRule, sReplacement, sInput).strip()

    def getVerb(self, input):
        if input in PersianStemmer.verbDic:
            vs = PersianStemmer.verbDic[input]
            if self.validation(vs.getPast()):
                return vs.getPast()
            return vs.getPresent()
        elif input in PersianStemmer.informalverbDic:
            vs = PersianStemmer.informalverbDic[input]
            if vs.getPast():
                return vs.getPast()
            return vs.getPresent()
        return ""

    def PatternMatching(self, input, stemList=[]):
        terminate = False
        s = ""
        sTemp = ""
        for rule in PersianStemmer._ruleList:
            if terminate:
                return terminate

            sReplace = rule.getSubstitution().split(";")
            pattern = rule.getBody()

            if not self.isMatch(input, pattern):
                continue

            k = 0
            for t in sReplace:
                if k > 0:
                    break

                s = self.extractStem(input, pattern, t)
                if len(s) < rule.getMinLength():
                    continue

                if rule.getPoS() == 'K':  # Kasre Ezafe
                    if len(stemList) == 0:
                        sTemp = self.getMokassarStem(s)
                        if sTemp:
                            # , pattern + " [جمع مکسر]")
                            stemList.append(sTemp)
                            k = k + 1
                        elif self.normalizeValidation(s, True):
                            stemList.append(s)  # , pattern)
                            k = k + 1
                        else:
                            pass
                            # addToLog("", pattern + " ::" + s + "}")
                elif rule.getPoS() == 'V':  # Verb
                    sTemp = self.verbValidation(s)
                    if len(sTemp) == 0:
                        stemList.append(s)  # pattern + " : [" + sTemp + "]"
                        k = k + 1
                    else:
                        pass
                        # addToLog("", pattern + " ::تمام وندها}")
                else:
                    if self.normalizeValidation(s, True):
                        stemList.append(s)
                        if rule.getState():
                            terminate = True
                            k = k + 1
                    else:
                        pass
                        # addToLog("", pattern + " ::" + s + "}")
        return terminate

    def verb_pattern_matching(self, input):
        for rule in PersianStemmer.verb_rule_list:
            sReplace = rule.getSubstitution().split(";")
            pattern = rule.getBody()

            if not self.isMatch(input, pattern):
                continue

            k = 0
            for t in sReplace:
                if k > 0:
                    break

                s = self.extractStem(input, pattern, t)
                if len(s) < rule.getMinLength():
                    continue

                s2 = self.getVerb(s)
                if s2:
                    return s2
                else:
                    continue

        return ""

    def multiple_run(self, input):
        terminate = False
        while not terminate:
            output = self.run(input)
            if input == output:
                terminate = True
            else:
                input = output

        return output

    def run(self, input):
        input = self.normalization(input).strip()

        if not input:
            return ""

        # Integer or english
        if Utils.isEnglish(input) or Utils.isNumber(input) or len(input) <= 2:
            return input

        if self.enableCache and input in self.cache:
            return self.cache[input]

        s = self.getMokassarStem(input)
        if s:
            # addToLog(s/*, "[جمع مکسر]"*/)
            # stemList.add(s)
            if self.enableCache:
                self.cache[input] = s
            return s

        input = self.normalizeValidation(input, False)

        s = self.getMokassarStem(input)
        if s:
            # addToLog(s/*, "[جمع مکسر]"*/)
            # stemList.add(s)
            if self.enableCache:
                self.cache[input] = s
            return s

        stemList = []
        terminate = self.PatternMatching(input, stemList)

        if self.enableVerb:
            s = self.getVerb(input)
            if s:
                stemList = [s]
            else:
                s = self.verb_pattern_matching(input)
                if s:
                    stemList = [s]

        if len(stemList) == 0:
            if self.normalizeValidation(input, True):
                # stemList.add(input, "[فرهنگ لغت]")
                if self.enableCache:
                    self.cache[input] = input  # stemList.get(0))
                return input  # stemList.get(0)
            stemList.append(input)  # , "")

        if terminate and len(stemList) > 1:
            return self.nounValidation(stemList)

        if self.patternCount != 0:
            stemList.sort(reverse=self.patternCount >= 0)
            stemList = stemList[abs(self.patternCount)-1:]

        if self.enableCache:
            self.cache[input] = stemList[0]

        return stemList[0]

    def nounValidation(self, stemList):
        stemList.sort()
        lastStem = stemList[-1]

        if lastStem.endswith("ان"):
            return lastStem
        else:
            firstStem = stemList[0]
            secondStem = stemList[1].replace(" ", "")

            for sSuffix in PersianStemmer.suffixZamir:
                if secondStem == firstStem + sSuffix:
                    return firstStem

        return lastStem
