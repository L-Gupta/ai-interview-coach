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
