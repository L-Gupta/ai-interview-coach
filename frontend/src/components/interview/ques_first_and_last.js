const introPrompts = [
  (name) => `Good morning ${name}, how are you doing today? Can you tell me a little about yourself?`,
  (name) => `Hi ${name}, let's begin with a quick introduction. Tell me about yourself.`,
  (name) => `Welcome ${name}. Let's start off with a quick introduction about yourself.`,
  (name) => `Hey ${name}, could you walk me through your background and interests?`,
  (name) => `Hello ${name}! Why don't you kick things off by telling me a bit about yourself?`
];

export function generateFirstQuestion(name) {
  const index = Math.floor(Math.random() * introPrompts.length);
  return introPrompts[index](name.trim());
}

const farewells = [
  (name) => `Thanks ${name}, that wraps up our interview. We’ll review your responses and get back to you soon. Have a great day!`,
  (name) => `Alright ${name}, that’s the end of our questions. We appreciate your time and wish you all the best!`,
  (name) => `That concludes the interview, ${name}. Thanks for joining us and sharing your experiences.`,
  (name) => `We’ve reached the end of our session, ${name}. It was great speaking with you — have a wonderful day!`,
  (name) => `Thank you, ${name}. That’s all the questions we had today. We’ll be in touch soon!`,
  (name) => `That’s it for today, ${name}. Thank you for your time and thoughtful answers.`,
  (name) => `Thanks ${name}, this brings our interview to a close. Wishing you the very best moving forward!`
];

export function generateLastQuestion(name) {
  // Pick a random message
  const randomIndex = Math.floor(Math.random() * farewells.length);
  return farewells[randomIndex];
}