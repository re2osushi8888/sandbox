import {it,expect } from 'bun:test';
import {bg} from './main';

it('[5,4,3]の時、剪定する枝は1', () => {
  const list = [5,4,3]
  expect(bg(list)).toBe(1);
})
it.skip('[3,4,5]の時、剪定する枝は1', () => {})
it.skip('[5,4,5,6,7]の時、剪定する枝は1', () => {})
it.skip('[5,4,5,6,7,8]の時、剪定する枝は2', () => {})
it.skip('[3,3,4]の時、剪定する枝は1', () => {})

