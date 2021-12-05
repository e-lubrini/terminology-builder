# terminology-builder

This is the repository for the project  is that of developing a term identification system. Our solution was tested
on the domain of botanics, but can be easily adapted to others domains, with similar accuracy
results to be expected. we collected a corpus of at 25 articles on topics belonging to our chosen
domain and extracted automatically the terms from such corpus first by implementing a rule-
based system and then by training a model using some golden annotation.
The rule-based system used POS tags in order to detect common term patterns in the article,
while the model us


Domain: botanics

Article list: [as-botanicalstudies.springeropen.com](https://as-botanicalstudies.springeropen.com/articles)

Assignment: [♦slides](https://arche.univ-lorraine.fr/pluginfile.php/2203811/mod_resource/content/3/project2021.pdf)

# Pipeline

The pipeline starts with the collection of n articles (suggested \(n > 20\)) by passing the number of articles to the class \code{ArticlesExtraction} and calling its \code{extract} method. This returns a dictionary of articles of length \(n\) where each key and value are the title and text of an extracted article, respectively.

In order to extract terms from the texts, we use the class \code{RuleBasedExtractor}, calling it without any arguments, and then use its \code{extract} function by passing the texts as arguments. The resulting output is a list of terms.

The next step in the pipeline is the manual term annotation. In order to ease the process, we provided tools to save the \(n\) most common term candidates in a .txt and the possibility to import a file of manually filtered terms for the following experiments.

Thanks to the class \code{TerminologyTree} we can create a tree structure filled with words from the terminology by calling the function \code{fill\_terminology\_tree} and passing it the terminology and an empty tree as arguments. We are then ready to annotate the text by looking up words in the tree.

Using the \code{Annotator} class, we can access the \code{annotate} method, which takes the tree and a text as an argument and returns the annotated text in the form of a list of triples, each containing three strings: (1) the token, (2) the POS, and (3) the BIOS label. 
