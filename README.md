# Bioschemas ProfileGenerator
Experimental scripts for creating a new Bioschemas Profile

## Installation

If you have Conda/[BioConda](https://bioconda.github.io/) the below should hopefully work:

```shell
    git clone https://github.com/BioSchemas/ProfileGenerator
    cd ProfileGenerator
    conda env create
    conda activate profilegenerator
    type python  ## /home/stain/miniconda3/envs/profilegenerator/bin/python
    python setup.py install
```

## Usage

```
conda activate profilegenerator
python setup.py install  # reinstall on code update
bioschema-profilegen -v
bioschema-profilegen -h
bioschema-profilegen Dataset FancyDataset
```

If you don't have Conda, or use virtualenv or similar, then `setup.py` lists the Python dependencies. This code has been tested with Python 3.8.

You can also look auto-generated example for a particular schemaorg type or property:

```
schemaorg-example author
schemaorg-example Dataset
```

## License

MIT License <https://spdx.org/licenses/MIT>
  
Copyright (c) 2020 Heriot-Watt University, UK  
Copyright (c) 2020 The University of Manchester, UK

See [LICENSE](LICENSE) for details.
