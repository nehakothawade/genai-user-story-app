const { GoogleGenerativeAI } = require("@google/generative-ai");
require("dotenv").config();

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

const model = genAI.getGenerativeModel({
  model: "gemini-1.5-flash"
});

async function generateUserStories(requirementText) {

  // Step 1: Extract structured intent
  const analysisPrompt = `
You are a senior business analyst.

Analyze the following requirement and extract:
1. Functional requirements
2. Non-functional requirements
3. Pain points
4. Ambiguities

Requirement:
"${requirementText}"

Respond in JSON format.
`;

  const analysisResult = await model.generateContent(analysisPrompt);
  const analysisText = analysisResult.response.text();

  // Step 2: Convert into atomic user stories
  const storyPrompt = `
You are an Agile Product Owner.

Using the following analysis:

${analysisText}

Generate structured user stories.

Rules:
- Must follow format: As a [user], I want [goal], so that [benefit]
- Keep stories atomic
- Include measurable acceptance criteria
- Identify missing information
- Ask clarification questions
- Include edge cases
- Return structured JSON

Format:
{
  "userStories": [
    {
      "story": "",
      "acceptanceCriteria": [],
      "edgeCases": [],
      "clarificationsNeeded": []
    }
  ]
}
`;

  const storyResult = await model.generateContent(storyPrompt);
  return storyResult.response.text();
}

module.exports = { generateUserStories };
