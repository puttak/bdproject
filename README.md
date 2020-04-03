bdproject
==============================
This is the repository of our 2020 course project in **ETH Zurich's 
Big Data and Public Policy** course. The team members are 
[Niklas Stolz](https://www.linkedin.com/in/niklas-stolz-54153114b/) 
and [Felix Zaussinger](https://www.linkedin.com/in/felix-zaussinger-3bb62510b/). 
The project is being supervised by 
[Malka Guillot](https://malkaguillot.weebly.com/) and 
[Elliot Ash](https://elliottash.com/), of ETH Zurich's Center for Law
& Economics' [Law, Economics and Data Science Group](https://lawecondata.ethz.ch/).

Research Question
------------
**Which policies are most effective in combating COVID-19? 
Leveraging panel regression and sentiment analysis in the United States.**

Abstract
------------
Needless to say, the success in combating COVID-19 depends on the timing and 
extent of well-informed policies, guidelines and laws. However, also societal 
sentiment plays a big role. It is crucial whether top-down imposed measures are 
responsibly obeyed by society or merely derided. In select cases, governments 
have been rather slow in imposing national measures, which led to states, 
counties and municipalities taking the lead within their scope of governance. 
This semester project aims at disentangling the effect of policy responses to 
the COVID-19 pandemic in the US by applying panel regression and sentiment 
analysis.

In a first step, we manually code policy interventions such as guidelines, laws, 
and health infrastructure expansions at the state-level over time. 
Second, we collect state level data on demographic and socioeconomic 
characteristics, health-related infrastructure, weather, et cetera, which will 
be used as control variables in the regression framework. Third, we apply 
sentiment analysis to at least two major newspapers loosely representative of 
conservative and liberal agendas and reader bases. In this way we intend to get 
a hand on the societal sentiment with respect to the pandemic: we exploit how 
people talk about the topic, which might correlate with how they actually 
behave. Sentiment features will contribute to the model as additional 
explanatory variables.

As independent variables, we will use state-level data on confirmed COVID-19 
infections and deaths from the 
[CSSE data base at John Hopkins University](https://github.com/CSSEGISandData/COVID-19). 
In a first run, we will formulate the panel regression framework in a fully 
parsimonious way, i.e., by including single policies as dummy variables. If this 
doesn't yield plausible results, we will try to aggregate the policy 
interventions along a set of relevant dimensions, such as magnitude of 
restrictiveness and extent (to be defined). 

Our analysis aims at answering questions such as: what would have 
happened if policy X had been applied earlier? What if the response had been 
better coordinated top-down? If meaningful results can be obtained, this could 
theoretically contribute to drawing well-informed conclusions out of the policy 
interventions of the past weeks and inform the policy response for the months 
to come.

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── logs               <- Log files, for now of the main programme pipeline.
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or transform data
    │   │   └── download.py
    │   │   └── reader.py
    │   │   └── split_csse_data.py
    │   │   └── structures.py    
    │   │
    │   ├── features       <- Scripts to turn processed data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   ├── utils       <- Utility functions to be used elsewhere.
    │   │   └── paths.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
