# Program Snapshot Data Toolkit

This codebase serves as a starting point for collecting, sharing and analyzing log data collected from students or users writing programs, including snapshots of code. Specifically, it supports collecting and analyzing data in the common [ProgSnap2 format](https://cssplice.org/progsnap2/) ([Price et al, 2020](https://dl.acm.org/doi/10.1145/3341525.3387373)). The goal of the work is to support computing education research, educational data mining and learning analytics, and it is presented as part of the [SPLICE project](https://cssplice.org/).

Possible use-cases include:
* **Analytics**: I have a research question that I want to answer using programming log data.
  * The Toolkit connects with a number of ready-to-analyze datasets in a shared format, and provides starter code and examples for how to dig into them.
* **Getting Started**: I want to see some examples of what programming log data analysis can do, and build on others' work rather than starting from scratch.
  * The Toolkit provides analysis code from prior work and examples of how to apply it so you can get started.
* **Replication**: I just found something interesting in my own programming dataset, and I want to know if the finding generalizes.
  * The Toolkit helps you replicate your analysis across diverse, multi-institutional datasets, and even to contribute your analysis back to the community in a reusable way.
* **Data Collection**: I'm planning to run a study and collect programming data.
  * The Toolkit offers a customizable starting point for a logger that follows best practices for capturing all the events and event properties you and others will need to understand your data. It uses the ProgSnap2 format, which is compatible with all analytics code provided in this repository.
* **Data Sharing**: I have a dataset and I want to share it. How can I make it most useful to others?
  * The Toolkit offers tools for converting data from any format to the common ProgSnap2 format, making it easier for others to analyze your code. It also offers best practices on how to document your dataset for sharing.

The toolkit is broken into a number of modules, which are largely for data collection and data analysis

# Quickstart
* Clone this repository
  * You can make a fork and modify this repository
  * Or you can install it as a submodule of a larger repo
* Install Python 3.11.11 or later
  * *Optional*: Create a virtual environment (venv or conda) for this project, to avoid dependency conflicts
* Install requirements with `pip install -r requirements.txt`
  * If you are planning to run the API for data collection, use `requirements-api.txt` instead.
  * If you are planning to improve and develop this repository, use `requirements-dev.txt` instead.
* Continue with the Data Analysis or Data Collection sections below, depending on your use case.

# Data Analysis
To do data analysis, you need a ProgSnap2-format dataset. You have two options:
1. Use an existing, compatible dataset, with a config file already included in the Toolkit.
2. Use your own dataset (see the Data Collection section below if you want to collect a new dataset).

## Use an Included Dataset

The Toolkit provides provides configuration files for loading existing public CS education datasets, including:
* [CodeWorkout / 2nd CSEDM Data Challenge Dataset](https://sites.google.com/ncsu.edu/csedm-dc-2021/dataset?authuser=0): `codeworkout`, including S19 and F19 semesters.
* [Falconcode](https://falconcode.dfcs-cloud.net/)
* [Codebench](https://codebench.icomp.ufam.edu.br/dataset/), including the S24 semester (more to be added)
* [Edwards' Keystroke Datasets](https://files.eric.ed.gov/fulltext/EJ1383373.pdf), including S19, F19 and F21.

They are described in more detail in [this document](https://docs.google.com/document/d/1zqO6hIFAUS1aEJ5TVaoMes_d4Oyearg8buLIC-Dfygk/edit?tab=t.0).

Example usage:
```python
from progsnap2.datasets import codeworkout

# Gets the configuration file for the F19 semester
# of the codeworkout dataset
config = codeworkout.F19
# Load the dataset, using the config
dataset = config.load('path/to/root/directory')

# Reads the first 20 rows of the main table
dataset.get_main_table_head(20)
```

The config itself contains other useful information, beyond just for loading the dataset, for example:
* `programming_language`: The programming language used by the dataset
* `granularity`: The granularity at which snapshots were collected (e.g., submission-level, keystroke-level)
* `grades_link_table_name` / `final_grade_column`: The LinkTable and column where students' final grade is stored (if available)
* Which columns are recommended to use to identify timestamps, problems, etc.

## Using Another Dataset

If you have a ProgSnap2 dataset not included above that you want to load, you need to define a [PS2DataConfig](src\progsnap2\database\config.py). You can do so in a .yaml file or using code. This config defines the format of your ProgSnap2 dataset and where to find it. See [this notebook](src\progsnap2\examples\custom_config.ipynb) for an example of how to define your own `PS2DataConfig`. Note that you may need to add some preprocessors to ensure compatibility.

# Data Collection

The Toolkit can also support collecting or converting a dataset. The easiest way to do so is to use or modify the included [FastAPI data collection server](src\progsnap2\api\main.py).

To run this server, first make sure you have install the `requirements-api.txt` dependencies, and then run: `run_api.bat` or `run_api.sh`.

This server uses a config file that control how it writes the data it collects. By default it uses [api_config.yaml](src\progsnap2\api\api_config.yaml). The data model for this config is the [PS2APIConfig](src\progsnap2\api\config.py), which itself extends the various other config files. By default, this will log data to a SQLite database in the `test-data` folder, but it can be configured to use a SQL database instead. Note that writing to a CSV file is not currently supported, as this is not feasible in a live data collection context and the Toolkit can read directly from SQLite or SQL databases; however, a database can be exported to CSV files if desired.

It is recommended to use a program that can browse your chosen database type, such as [phpmyadmin](https://www.phpmyadmin.net/) for SQL or [DBBrowser](https://sqlitebrowser.org/) for SQLite. The sample API provided is write-only and does not support viewing the dataset, though you can use the Toolkit to load the dataset as described above.

The server's API is minimal and can be found at http://127.0.0.1:8000/docs.

The server will validate events sent to it. By default, it will raise warnings if invalid events are received but it will still log them if possible to avoid inadvertent data loss.

**Note**: The server does not include authentication. It should be seen as a starting point for prototyping, not a finished, secure server.

## Creating a Client

A sample client can be found in the [PST-SampleLogger](https://github.com/thomaswp/PST-SampleLogger) repository. This includes instructions for how to generate Typescript helper methods for logging all events and sending them to the server.

## Modifying the ProgSnap2 Spec with new Events and Columns

The ProgSnap2 spec is defined in a .yaml file, currently [progsnap2-v1.0.yaml](src\progsnap2\spec\versions\progsnap2-v1.0.yaml). You can modify this file to support logging new events, or including new columns. See the [ProgSnap2 format](https://cssplice.org/progsnap2/) for more details on how to do this.

Once you have modified the YAML file, the server will automatically support new events and columns. You can regenerate typescript files in your client to support these events. See [test.py](test.py) for some examples of code generation.

# Project Structure

This project contains a number of subpackages:
* `analytics`: Contains helper classes and functions for analyzing ProgSnap2 datasets and defining your own analytics.
* `api`: Contains a sample FastAPI server for collecting ProgSnap2 datasets.
* `converters`: Contains code used to convert existing public datasets into the ProgSnap2 format (or to modify ProgSnap2 datasets for full compatibility with the Toolkit).
* `database`: Contains helper classes and functions for reading and creating ProgSnap2 datasets in various formats, including .csv, SQLite and SQL.
* `datasets`: Contains config files with important properties of known, supported ProgSnap2 datasets that help with loading and analytics, as well as a base class to define your own.
* `examples`: Includes various notebooks to demonstrate features of the ProgSnapToolkit.
* `spec`: Defines the data model for a ProgSnap2 specification and includes helper classes and functions for loading a specification from a .yaml file. Also includes helpful enums for ProgSnap2 with attached documentation, and generator scripts to generate code files.