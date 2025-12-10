---
sidebar_position: 1
title: Create a Page
---

# Create a Page

In your Physical AI book framework, you can add **Markdown or React** files to `src/pages` to create **standalone pages** for topics or demonstrations:

- `src/pages/index.js` → `localhost:3000/` (homepage)  
- `src/pages/overview.md` → `localhost:3000/overview`  
- `src/pages/robots/movement.js` → `localhost:3000/robots/movement`  

## Create your first React Page

Create a file at `src/pages/robot-intro.js`:

```jsx title="src/pages/robot-intro.js"
import React from 'react';
import Layout from '@theme/Layout';

export default function RobotIntroPage() {
  return (
    <Layout>
      <h1>Introduction to Physical Robots</h1>
      <p>This page explains how embodiment shapes intelligence in Physical AI systems.</p>
    </Layout>
  );
}
