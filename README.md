# AI BOOK GENERATOR

**AI Book Generator** is a project that leverages large language models (LLMs) to generate complete books. By structuring the workflow as an autonomous agent system, it showcases the potential for creative and iterative processes driven by AI.

The primary goal of this project is to demonstrate how an LLM can produce high-quality, self-contained outputs, while also highlighting the differences between a simple LLM workflow and a more advanced agent-based system.

---

## **How It Works**

The process follows a structured pipeline designed to produce and evaluate books:

1. **Input Source**  
   - **User Input**: Users can provide prompts, themes, or topics to guide book generation.  
   - **Random Input**: Alternatively, random inputs can be selected from a predefined list to create a book from scratch.

2. **Writer Agent**  
   - This is the core generator that produces a full book based on the input. The output includes text structured into chapters, sections, and a cohesive narrative.

3. **Reviewer Agent**  
   - The reviewer evaluates the generated book, assigning a score based on criteria like coherence, creativity, grammar, and adherence to the input.  

4. **Filter**  
   - If the review score meets or exceeds a predefined threshold, the book is approved for release. Otherwise, it is discarded or sent back for iteration.  

5. **Output**  
   - Approved books are finalized into a PDF or other book-friendly formats, ready for publishing or sharing.

---

## **Why Use an Agent Framework?**

This project operates as an agent because of its ability to iterate and adapt based on feedback:  

- **Simple Workflow (Non-Agent)**:  
  In a standard LLM workflow, the process ends after generating a single book based on user input. This approach is straightforward but lacks adaptability.  

- **Agent Workflow (Closed Loop)**:  
  By feeding the review score and detailed feedback from the Reviewer Agent back into the Writer Agent, the system creates a feedback loop. The Writer Agent can use this information to improve its output iteratively, leading to better-quality books over time.  

This feedback loop aligns with the characteristics of an agent, as it involves **continuous interaction** with the environment (review and filtering process) and **goal-oriented behavior** (creating high-quality books).

---

## **Features**

- **Customizable Inputs**: Provide specific prompts or let the system create randomly themed books.  
- **Automated Evaluation**: Built-in reviewer ensures quality control.  
- **Feedback Integration**: Optional feedback loop for iterative refinement.  
- **Seamless Output**: Generate books in popular formats like PDF with minimal user intervention.  

---

## **Use Cases**

- **Creative Writing**: Quickly produce draft books for brainstorming or inspiration.  
- **Education**: Generate educational content on demand.  
- **Entertainment**: Create personalized stories or novels.  

---

## **Future Enhancements**

- **Dynamic Scoring Criteria**: Allow users to define custom evaluation metrics.  
- **Multi-Agent Collaboration**: Introduce specialized agents for tasks like content structuring or genre-specific writing.  
- **Interactive Review**: Enable users to intervene in the review process for more personalized outcomes.  
- **Publishing Integration**: Directly integrate with online platforms for seamless book publishing.  

---

## **Getting Started**

1. Clone the repository:  
   ```bash
   git clone https://github.com/yourusername/ai-book-generator.git
   ```

2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

3. Run the system:  
   ```bash
   python main.py
   ```

4. Follow the prompts to generate your book!

---

## **License**

This project is licensed under the [MIT License](LICENSE).
