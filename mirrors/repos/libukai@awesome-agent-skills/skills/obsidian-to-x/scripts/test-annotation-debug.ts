import { Lexer } from 'marked';

const markdown = `> [#6171] Safe YOLO Mode
> 您可以选择不监督 Claude，而是使用 \`claude --dangerously-skip-permissions\` 来绕过所有权限检查。`;

const tokens = Lexer.lex(markdown, { gfm: true, breaks: true });

console.log('=== Blockquote Token ===');
if (tokens[0]?.type === 'blockquote') {
  const bq = tokens[0] as any;
  console.log('Blockquote has', bq.tokens.length, 'tokens');
  
  if (bq.tokens[0]?.type === 'paragraph') {
    const para = bq.tokens[0];
    console.log('\n=== Paragraph Tokens ===');
    console.log('Paragraph has', para.tokens.length, 'tokens');
    
    para.tokens.forEach((token: any, i: number) => {
      console.log(`\nToken ${i}:`, {
        type: token.type,
        text: token.text || token.raw,
      });
    });
    
    if (para.tokens[0]?.type === 'text') {
      const text = para.tokens[0].text;
      console.log('\n=== First Text Token ===');
      console.log('Text:', JSON.stringify(text));
      const match = text.match(/^\[#\d+\]\s+(.*)$/);
      console.log('Match result:', match);
    }
  }
}
