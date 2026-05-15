import type { Preview } from '@storybook/react-vite';

import { authDecorator, routerDecorator, themeDecorator } from './decorators';

const preview: Preview = {
  decorators: [themeDecorator, routerDecorator, authDecorator],

  parameters: {
    layout: 'fullscreen',
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /date$/i,
      },
    },
    a11y: {
      context: '#storybook-root',
    },
  },
};

export default preview;