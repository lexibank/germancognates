import pathlib
import attr
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar as pb
from pylexibank import Lexeme
from pylexibank import FormSpec
from pyedictor import fetch
from lingpy import Wordlist

@attr.s
class CustomLexeme(Lexeme):
    Alignment = attr.ib(
            default=None,
            metadata={
                "datatype": "string",
                "separator": " "})

class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "germaniccognates"
    lexeme_class = CustomLexeme
    form_spec = FormSpec(separators="~;,/", missing_data=["∅"], first_form_only=True)
    
    def cmd_download(self, args):

        with open(self.raw_dir / "germanic.tsv", "w") as f:
            data = fetch("germanic", base_url="http://digling.org/edictor")
            f.write(data)
            
    def cmd_makecldf(self, args):
        # add bib
        args.writer.add_sources()
        args.log.info("added sources")        


        wl = Wordlist(str(self.raw_dir / "germanic.tsv"))
        concepts = {}
        for i, concept in enumerate(wl.concepts):
            idx = str(i+1) + "_" + slug(concept)
            args.writer.add_concept(
                    ID=idx,
                    Name=concept,
                    )
            concepts[concept] = idx


        # add language
        languages = args.writer.add_languages(lookup_factory="Name")
        args.log.info("added languages")

        # add data
        for idx in pb(wl, desc="cldfify", total=len(wl)):
            args.writer.add_form_with_segments(
                    Parameter_ID=concepts[wl[idx, "concept"]],
                    Language_ID=languages[wl[idx, "language"]],
                    Value=wl[idx, "counterpart"],
                    Form=wl[idx, "ipa"],
                    Segments=wl[idx, "tokens"],
                    Cognacy=wl[idx, "cogid"],
                    Alignment=wl[idx, "alignment"])

