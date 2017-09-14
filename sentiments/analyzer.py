import nltk

class Analyzer():
    """Implements sentiment analysis."""

    def __init__(self, positives, negatives):
        """Initialize Analyzer."""
        # TODO
        filePos = open(positives)
        pos_list = []
        for line in filePos:
            if line.startswith(";", 0) or str.isspace(line):
                continue
            else:
                pos_list.append(str.strip(line)) 
        self.positives = tuple(pos_list)
        fileNeg = open(negatives)
        neg_list = []
        for line in fileNeg:
            if line.startswith(";", 0) or str.isspace(line):
                continue
            else:
                neg_list.append(str.strip(line)) 
        self.negatives = tuple(neg_list)

    def analyze(self, text):
        """Analyze text for sentiment, returning its score."""
        # TODO
        tokenizer = nltk.tokenize.TweetTokenizer()
        tokens = tokenizer.tokenize(text)
        count = 0
        for c in tokens:
            c = c.lower()
            
            if c in self.positives:
                count += 1
            elif c in self.negatives:
                count -= 1
            else:
                continue
        
                
            
            
        return count
