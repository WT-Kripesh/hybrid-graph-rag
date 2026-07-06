# NLP-based DBMS: Natural Language Interface for Database Management

## Acknowledgments

We sincerely thank the **Project Management team** at our Department of Electronics and Computer Engineering, Pulchowk Campus, for providing a supportive learning environment. This project report is a testament to the dedication and collective efforts of all team members, each contributing their unique expertise and perspectives. We are deeply grateful to all those who have supported us throughout this journey.

Most importantly, we express our deepest gratitude to our project supervisor, **Prof. Daya Sagar Baral**, for his invaluable guidance, encouragement, and insightful feedback at every stage of this project. His unwavering support played a pivotal role in shaping the development process and refining our approach.

The authors also express sincere thanks to the Department of Electronics and Computer Engineering, Pulchowk Campus, for granting us the opportunity to embark on this project. In addition, we are deeply grateful to our teachers and peers whose encouragement, constructive critiques, and intellectual engagement have created a stimulating environment of academic excellence and innovation. Their support has been invaluable in helping us navigate the complexities of this project.

## Abstract

This report details the development and completion of our final year project titled "NLP based DBMS," a natural language interface for database management. The project utilizes two approaches for achieving results: a mapping-based query translation model employing NLP techniques and a fine-tuned transformer model to handle complex queries. Both models were successfully integrated with a user interface developed as a full-stack web application. The system was made fully functional and deployed on a virtual machine in the cloud.

**Keywords:** NLP, interface, translation, transformer, cloud

 

## 1. Introduction

### 1.1 Background

In the information age, efficient database management is critical. While traditional DBMS platforms (MySQL, PostgreSQL, Oracle) are powerful, they rely on Structured Query Language (SQL), which poses a barrier for non-technical users. Our project bridges this gap by integrating Natural Language Processing (NLP) into DBMS, allowing users to query databases using natural language, powered by a fine-tuned T5-small model.

### 1.2 Problem Statement

SQL requires technical proficiency, making basic operations difficult for non-technical users. Training is time-consuming, and even for experienced users, manual construction of complex queries is prone to errors. There is a societal need for intuitive, natural language interaction to improve data accessibility.

### 1.3 Objectives

* Design and implement an NLP module to parse and understand natural language queries.
* Gather, preprocess, and utilize extensive datasets for model validation.
* Utilize a transformer model to translate English queries into SQL.
* Develop a user-friendly web interface for query input and result display.

### 1.4 Scope

The system supports standard SQL functionalities: SELECT, DISTINCT, aggregate functions (COUNT, SUM), JOINs, logical/comparison operators, ORDER BY, and GROUP BY. The current implementation is specifically designed for MySQL.

 

## 2. Literature Review

### 2.1 Related Work

* **Transformer Models and T5:** State-of-the-art for text-to-SQL tasks. T5-small (60M parameters) is an efficient encoder-decoder model.
* **QueryGPT (Uber):** Uses LLMs and RAG to automate query generation, significantly reducing manual effort.
* **Qwen-2.5-Instruct (Alibaba):** Excels in complex SQL tasks and schema-less generation.
* **Academic Research:** Various studies have utilized pattern matching and intermediate query representations for translating natural language into SQL.

### 2.2 Related Theory

#### 2.2.1 NLP Techniques

* **Tokenization & Lemmatization:** Basic steps to normalize text for consistent analysis.
* **Syntactic Analysis:** Parsing grammatical structures to identify roles like subjects and predicates.
* **SQL Query Formation:** Mapping extracted attributes and conditions to valid SQL syntax.

#### 2.2.2 Transformer Architecture

Transformers use self-attention to weigh word importance, enabling parallel processing of sequences.

* **Self-Attention Mechanism:**

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$$


* **Encoder-Decoder Structure:** The encoder creates contextual representations, and the decoder generates output tokens.

#### 2.2.3 Evaluation Metrics

* **ROUGE:** Measures n-gram overlap between generated and reference summaries.
* **BLEU:** Assesses the fluency and accuracy of generated text.
* **Human & Execution Accuracy:** Subjective assessment and verification of actual query results.

 

## 3. Methodology

### 3.1 Query Translation Mechanism

* **Rule-Based Approach:** Integrates with database schema to map tokens (tables/columns) using tokenization and lemmatization.
* **Machine Learning Approach:** Utilizes a fine-tuned T5-small model for complex, natural language-to-SQL translation.

### 3.2 System Architecture & Integration

* **Database:** MySQL, accessed via `mysql.connector`.
* **Frontend:** React-based web application.
* **Backend:** Flask API, handling NLP processing, query translation, and database interaction.

### 3.3 ML-Based System Training

* **Dataset:** Gretel.ai Synthetic Text-to-SQL (100k records across 100 domains).
* **Preprocessing:** Schema cleaning (extracting table structures) and feature selection (Query + Schema $\rightarrow$ SQL).
* **Tokenization:** T5Tokenizer with max lengths of 512 (input) and 256 (output).
* **Training:** Fine-tuned on Kaggle using a P100 GPU with a learning rate of $3 \times 10^{-4}$.

 


## 3. Methodology: Evaluation Protocol

### 3.1 Metrics

To ensure a robust assessment of our query translation capabilities, we employ the following metrics:

* **BLEU Score:** Serves as the primary metric for assessing the textual accuracy of the generated SQL queries against the reference ground truth.
* **Execution Accuracy:** Measures the closeness of the model's query results compared to the actual database results. This metric is a superior indicator of the model's real-world utility, as it accounts for the fact that a single semantic request can often be implemented using multiple valid SQL variations.

### 3.2 Validation

A 20% holdout dataset was used to evaluate the model's generalization capabilities across varying levels of SQL complexity.

 

## 4. System Design

### 4.1 NLP-Based System

The rule-based NLP system processes natural language queries by extracting keywords and filtering out redundant data. The workflow consists of a **Processing Phase** and a **Mapping Phase**.

#### Processing Phase

1. **Tokenization:** Input is broken into individual words via a custom Python-based word-level tokenizer.
2. **Lemmatization:** Tokens are reduced to their root forms (lemmas) to standardize the input, ensuring better matching accuracy than simple stemming.
3. **Syntactic Analysis:** Each token is analyzed for its grammatical role and tagged with its Part of Speech (POS).
4. **Parsing/Chunking:** Tokens are grouped into meaningful phrases (e.g., "sales report" as a noun phrase) to facilitate extraction of significant information.

#### Mapping Phase

1. **Attribute Identification:** The system maps the processed tokens to database elements, identifying tables and filter conditions.
2. **SQL Query Formation:** Syntactically correct SQL is constructed based on the identified attributes.

 

### 4.2 ML-Based System

#### Architecture

The ML-based system follows a three-tier architecture:

* **Frontend (React Web Application):** Provides an intuitive interface for user authentication, database selection, and natural language input.
* **Processing Tier (Flask):** The core engine that receives the natural language query and schema metadata. It leverages a fine-tuned T5-small model to translate the input into SQL.
* **Database Tier (MySQL):** Stores the data and schema, executing the translated SQL and returning results to the interface.

 

## 5. Discussion: Query Generation Process

### 5.1 NLP-Based SQL Generation

* **Table Extraction:** The system uses a Longest Common Subsequence (LCS) algorithm to match user query tokens against available database tables. The table with the highest "neighboring count" of matching characters is selected as the most relevant source.
* **Column Extraction:** Similar to table matching, the system calculates the LCS and neighboring counts between tokens and column names. Only columns meeting a similarity threshold are selected.
* **WHERE/ORDER BY Clauses:** The system uses keyword-based heuristics to isolate conditions (like "greater than") and sorting instructions (like "ascending"), mapping them to standard SQL operators and clauses.

### 5.2 Results and Performance

The fine-tuned T5-small model demonstrates significant performance improvements over the base model.

#### Performance Comparison (BLEU Scores)

| Metric | Initial Score | After Fine-tuning |
|   |   |   |
| BLEU-1 | 80.000 | 98.413 |
| BLEU-2 | 12.500 | 90.323 |
| BLEU-3 | 8.333 | 80.328 |
| BLEU-4 | 6.250 | 70.000 |
| **BLEU Overall** | **15.107** | **84.082** |

 

## 6. Limitations and Future Enhancements

### 6.1 Limitations

* **AI Hallucination:** The model may generate syntactically correct SQL that references imaginary table attributes.
* **Limited Vocabulary:** T5-small's constraints may struggle with specialized domain terminology.
* **Complex Query Performance:** The model currently lacks the depth to handle advanced SQL features like nested subqueries or complex multi-table joins consistently.

### 6.2 Future Enhancements

* **Metric Shift:** Transitioning from BLEU to Execution Accuracy as the primary benchmark.
* **UI/UX:** Improving interface responsiveness and visual clarity.
* **Dataset Expansion:** Incorporating real-world database schemas and labeled datasets from academic sources to improve generalization.
