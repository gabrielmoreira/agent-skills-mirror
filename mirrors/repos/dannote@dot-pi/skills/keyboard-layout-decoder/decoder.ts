#!/usr/bin/env node
import ru from 'convert-layout/ru'

function decode(text: string): string {
  return /[а-яё]/i.test(text) ? ru.toEn(text) : ru.fromEn(text)
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2)
  if (!args.length) {
    console.log('Usage: decoder.ts <text>')
    process.exit(1)
  }
  console.log(decode(args.join(' ')))
}
