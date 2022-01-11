# Public Analysis Database configuration repository
[![PAD](https://img.shields.io/static/v1?style=plastic&label=Recasting&message=PublicAnalysisDatabase&color=blue)](http://madanalysis.irmp.ucl.ac.be/wiki/PublicAnalysisDatabase)

This repository includes metadata required to configure PAD when downloaded in 
[MadAnalysis 5](https://github.com/MadAnalysis/madanalysis5) workspace. 
[MadAnalysis 5](https://github.com/MadAnalysis/madanalysis5) allows the installation of various 
recast and validated analyses where each analysis recast 
can be generated via a different detector simulator, namely Delphes or 
[MadAnalysis 5](https://github.com/MadAnalysis/madanalysis5) 's native detector 
simulator, so-called [SFS](https://arxiv.org/abs/2006.09387). These analyses can be recast by anyone 
who wishes to contribute to PAD (please see the 
[related issues section](https://github.com/MadAnalysis/madanalysis5/issues/new?assignees=&labels=PAD&template=code-submission-to-public-analysis-database.md&title=) 
for submitting a new analysis). Due to the variety of simulations 
and system settings, [MadAnalysis 5](https://github.com/MadAnalysis/madanalysis5) requires a detailed 
metadata configuration to install the analysis codes and their validation material properly. 
This repository is designed to build such information flow 
to [MadAnalysis 5](https://github.com/MadAnalysis/madanalysis5) during the toolset installation.


## Metadata structure

```python
[
    {
        "name"          : "analysis name",
        "description"   : "analysis description",
        "code_url"      : "location of the code",
        "detector_card" : "detector card url",
        "padversion"    : "PAD version of the analysis e.g. vSFS, v1.2, v1.1 etc.",
        "ma5version"    : "minimum madanalysis version required by the analysis",
        "gcc"           : "minimum c++ version required by the analysis",
        "bibtex"        : [
            "bibliography dedicated to the analysis"
        ]
    },
    { ... },
]
```