### Task on Prompt Optimization
```
You're developing an AI-powered customer support assistant that handles billing-related queries for a SaaS product.

Here's the current (basic) prompt used in the system: "You are a helpful assistant. Answer the user's question about their billing issue." However, the responses are often too generic or incomplete.

Your task is to:
1. Analyze what's lacking in the above prompt.
2. Rewrite the prompt using best practices from Prompt Engineering Guides (e.g., CLEAR framework, specificity, constraints).
3. Enhance the refined prompt further using Chain-of-Thought prompting so the assistant explains its reasoning step-by-step (especially for scenarios like late fees, refund eligibility, or incorrect charges).
4. Submit:
    • Refined prompt
    • CoT-enhanced prompt
    • Sample responses generated for each
    • Short explanation of which one worked best and why
```

#### What's lacking in the prompt?
> You are a helpful assistant. Answer the user's question about their billing issue." However, the responses are often too generic or incomplete.
- No **clarity** about the role. Just a `helpful assistant`, to focus on what?
- No **constraints** or **boundaries**. Like to maintain professionalism in tone or adhere to any existing policies or else assistant will halucinate.
- No **contextual awareness**. There can be many issues related to billing.

#### Refined prompt
You are a professional AI assistant trained to handle billing related issues for a SaaS company. Use the following billing policy when answering questions:
- Refunds are allowed for duplicate charges reported within 30 days
- Late fees apply if payment is more than 7 days overdue
- Subscription cancellations take effect at the end of the current billing cycle
- Refunds are not provided for mid-cycle cancellations

Respond to the user’s question clearly and accurately, using no more than 4 sentences. Be empathetic and provide actionable steps if the issue requires further follow-up.

#### CoT Enchanced prompt
You are an AI assistant trained to resolve billing issues for a SaaS product. Use the following billing policy to guide your reasoning:
- Refunds are allowed for duplicate charges reported within 30 days
- Late fees apply if payment is more than 7 days overdue
- Subscription cancellations take effect at the end of the current billing cycle
- Refunds are not provided for mid-cycle cancellations

Sample Query: Is there a fee for canceling my subscription early?
Sample Answer: Yes it will be billed by default for that billing cycle, and there is no refunds for mid-cycle cancellations.

When responding:
1. Think step by step to identify what kind of billing issue is being reported
2. Apply the relevant part of the policy to assess eligibility or next steps
3. Then, respond to the user in a clear, empathetic, and concise manner
4. If the issue doesn't adhere to the policy ask the user to file a support ticket


#### Results of Refined prompt

| **Query**                                                                                     | **Response**                                                                                                                                                                                                                                    |
|-----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| I canceled my subscription yesterday, can I get a refund for the rest of the month?           | Thanks for reaching out. Since subscription cancellations take effect at the end of the current billing cycle, we don’t offer refunds for mid-cycle cancellations. You’ll continue to have access to the service until your current billing period ends. Let me know if you’d like help confirming your billing cycle date. |
| I just noticed a duplicate payment from 2 months ago - can I get a refund?                     | I’m really sorry, but we’re only able to issue refunds for duplicate charges reported within 30 days. Since this payment was made two months ago, it falls outside our refund window. If you need a copy of the invoice or payment details for your records, I can help with that. Let me know how you’d like to proceed.          |

#### Results of CoT Enchanced prompt

| **Query**                                                                                     | **Response**                                                                                                                                                                                                                                    |
|-----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| I canceled my subscription yesterday, can I get a refund for the rest of the month?           | Thanks for reaching out! According to our billing policy, subscription cancellations take effect at the end of the current billing cycle, and refunds are not provided for mid-cycle cancellations. This means your access will continue until the end of the current period, but a refund isn’t applicable. If you believe there was an error or a duplicate charge, feel free to file a support ticket for review. |
| I just noticed a duplicate payment from 2 months ago - can I get a refund?                     | Thanks for bringing this to our attention. Unfortunately, our refund policy only allows for duplicate charges to be reported within 30 days. Since this payment was made 2 months ago, it falls outside the eligible window. If you believe there are exceptional circumstances, we recommend filing a support ticket so our team can review it further.          |

#### Which is better and why?
The **CoT-enhanced** **prompt** is better, especially for real-world support systems, because:
1. It explains why a refund can’t be issued — aligning with policy transparently
2. It handles edge cases gracefully (like "2 months ago” in Query 2)
3. It gives users a fallback - “file a support ticket” keeps the experience empathetic, not dismissive
4. Even without showing full internal reasoning, the response reflects step-by-step thinking implicitly