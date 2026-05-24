# TODO

Use plain TODO items for simple queues:

- [ ] Example task

Use optional hints when orchestration matters:

- [ ] Example React task #react #ui files:app/example/page.tsx,components/example.tsx
- [ ] Example docs follow-up #docs depends:example-react-task
- [ ] Example blocked item #blocked

Supported hints:

- `#tag` groups tasks and helps skill routing.
- `files:path-a,path-b` helps detect overlap.
- `depends:task-id-or-slug` forces sequencing.
- `#blocked` keeps the item out of the runnable queue.
