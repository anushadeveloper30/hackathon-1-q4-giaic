require('dotenv').config();
const express = require('express');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');
const { GoogleGenerativeAI } = require('@google/generative-ai');

const app = express();
const port = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

// Function to recursively read all markdown files from a directory
async function readMarkdownFiles(dir) {
    let combinedContent = '';
    const files = await fs.readdir(dir, { withFileTypes: true });

    for (const file of files) {
        const fullPath = path.join(dir, file.name);
        if (file.isDirectory()) {
            combinedContent += await readMarkdownFiles(fullPath); // Recurse into subdirectories
        } else if (file.isFile() && file.name.endsWith('.md')) {
            const content = await fs.readFile(fullPath, 'utf8');
            combinedContent += `
--- FILE: ${fullPath} ---
${content}
`;
        }
    }
    return combinedContent;
}

app.post('/chat', async (req, res) => {
    const userMessage = req.body.message;

    if (!userMessage) {
        return res.status(400).send('Message is required.');
    }

    try {
        if (!process.env.GEMINI_API_KEY || process.env.GEMINI_API_KEY === 'your_key_here') {
            const errorMessage = "GEMINI_API_KEY is not set or is using the placeholder. Please set your actual API key in the .env file.";
            console.error(errorMessage);
            return res.status(500).json({ error: errorMessage });
        }

        const bookContent = await readMarkdownFiles('docs');
        const prompt = `You are an AI assistant specialized in Anusha's book content.
        Your knowledge is strictly limited to the provided book content.
        Always strive to provide comprehensive and relevant answers *solely* based on the provided book content.
        If a question is outside the scope of the book content, you MUST respond with "Mera ilm sirf Anusha ki is book tak mehdood hai."
        Do not provide any information or opinions not found in the book.

        --- START OF BOOK CONTENT ---
        ${bookContent}
        --- END OF BOOK CONTENT ---

        User's question: ${userMessage}

        Your answer:`;

        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();
        res.json({ reply: text });

    } catch (error) {
        console.error('Error processing chat:', error);
        // Send the actual error message to the frontend for better debugging
        res.status(500).json({ error: 'Failed to get response from AI.', details: error.message });
    }
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
