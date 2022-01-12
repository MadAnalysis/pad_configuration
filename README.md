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

## Installation 

 - `$ pip install -e .` or `$ make install` 

## Metadata structure

```python
[
    {
        "name"          : "analysis name",
        "description"   : "analysis description",
        "url"           : {
            "cpp"      : "location of the code",
            "header"   : "location of the header file",
            "info"     : "location of the info file",
            "json"     : [
                {
                    "name" : "name of the json extension",
                    "url" : "location of the json file for full likelihoods"
                }
            ],
            "detector" : {
                "name" : "name of the detector card",
                "url" : "location of the detector card"
            }
        },
        "padversion"    : "PAD version of the analysis e.g. vSFS, v1.2, v1.1 etc.",
        "ma5version"    : "minimum madanalysis version required by the analysis",
        "gcc"           : "minimum c++ version required by the analysis",
        "bibtex"        : [
            "bibliography dedicated to the analysis"
        ]
    }
]
```

## Usage
```python
from pad_configuration import Configuration
config = Configuration("PADForSFS")
print(config)
```
will output the following;
```
#    Analysis            | Description
#                        |
atlas_exot_2018_05       | ATLAS - 13 TeV - di-jet resonance with a photon (76.8/fb)
atlas_susy_2016_07       | ATLAS - 13 TeV - multijet + met (36.1/fb)
atlas_susy_2017_04_2body | ATLAS - 13 TeV - displaced vertices with opposite charge leptons, 2-body decays (32.8/fb)
atlas_susy_2017_04_3body | ATLAS - 13 TeV - displaced vertices with opposite charge leptons, 3-body decays (32.8/fb)
atlas_susy_2018_31       | ATLAS - 13 TeV - multibottoms + MET (139/fb)
atlas_conf_2019_040      | ATLAS - 13 TeV - multijet + met (139/fb)
cms_sus_16_048           | CMS   - 13 TeV - Soft dilepton (35.9/fb)
cms_exo_16_022           | CMS   - 13 TeV - Displaced leptons (2.6/fb)
```

## TODO
 - [ ] Expand the documentations
 - [ ] Add individual bibliographies to each entry
 - [ ] Add `PADForMA5tune`