export default {
	paths: ['e2e/features/*.feature'],
	import: ['e2e/step_definitions/*.steps.ts'],
	loader : ['ts-node/esm']
};
