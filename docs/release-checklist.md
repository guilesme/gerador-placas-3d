# Checklist de Release

Use este checklist antes de criar uma tag ou GitHub Release.

## 1. Pre-release

- [ ] Confirmar que a branch correta esta atualizada.
- [ ] Confirmar que nao ha alteracoes inesperadas em `git status`.
- [ ] Revisar `docs/bug-and-fix-tracker.md`.
- [ ] Atualizar `CHANGELOG.md`.
- [ ] Atualizar `README.md` se o uso mudou.
- [ ] Atualizar `spec.md` se comportamento funcional mudou.
- [ ] Confirmar se a versao nova e patch, minor ou major.

## 2. Testes

- [ ] Rodar `python -m py_compile src/web/app.py src/web/validation.py src/web/plate_service.py src/blender/generator.py src/blender/threemf_exporter.py`.
- [ ] Rodar `python -m unittest discover -s tests -v`.
- [ ] Gerar uma placa simples em ambiente com Blender.
- [ ] Gerar uma placa multilinha.
- [ ] Validar download do `.3mf`.
- [ ] Abrir/importar arquivo no Bambu Studio quando possivel.
- [ ] Testar rollback ou confirmar tag anterior.

## 3. Documentacao

- [ ] `CHANGELOG.md` contem a versao.
- [ ] Bugs corrigidos foram marcados como `Fixed` ou `Verified`.
- [ ] Novos bugs descobertos foram registrados.
- [ ] Instrucoes de uso continuam corretas.
- [ ] Screenshots foram atualizados se a UI mudou.

## 4. Criar Tag

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

## 5. GitHub Release

Incluir:

- resumo;
- mudancas principais;
- bugs corrigidos;
- testes executados;
- riscos conhecidos;
- instrucoes de rollback;
- link para changelog.

## 6. Pos-release

- [ ] Confirmar que a tag aparece no GitHub.
- [ ] Confirmar que a release aparece no GitHub.
- [ ] Criar proxima secao `Unreleased` no `CHANGELOG.md`.
- [ ] Atualizar roadmap se necessario.
