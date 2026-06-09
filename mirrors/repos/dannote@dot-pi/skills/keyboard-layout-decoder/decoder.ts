#!/usr/bin/env bun
import ru from 'convert-layout/ru'

function decode(text: string): string {
  return /[а-яё]/i.test(text) ? ru.toEn(text) : ru.fromEn(text)
}

if (import.meta.main) {
  const args = Bun.argv.slice(2)
  if (!args.length) {
    console.log('Usage: decoder.ts <text>')
    process.exit(1)
  }
  console.log(decode(args.join(' ')))
}
