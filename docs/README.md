# Documentacao do Projeto

Esta pasta concentra a documentacao operacional do `gerador-placas-3d`: governanca, versionamento, bugs conhecidos, plano de testes, releases e roadmap.

Este arquivo nao substitui o `README.md` da raiz. O README da raiz deve continuar sendo a vitrine publica do projeto no GitHub; este arquivo e apenas o indice interno da documentacao tecnica.

O objetivo e manter a aplicacao evoluindo de forma profissional, com rastreabilidade suficiente para:

- saber o que esta funcionando hoje;
- planejar melhorias sem quebrar o uso atual;
- registrar bugs, decisoes e correcoes;
- criar releases recuperaveis via Git;
- demonstrar maturidade tecnica no GitHub.

## Indice

- [Governanca de Desenvolvimento](development-governance.md)
- [Versionamento e Releases](versioning-and-releases.md)
- [Rastreador de Bugs e Fixes](bug-and-fix-tracker.md)
- [Estrategia de Testes](testing-strategy.md)
- [Log de Verificacao](verification-log.md)
- [Roadmap](roadmap.md)
- [Visibilidade no GitHub](github-visibility.md)
- [Checklist de Release](release-checklist.md)

## Estado Atual

O projeto esta funcional para o proposito atual: gerar placas 3D em formato `.3mf` para o fluxo de impressao definido.

Antes de aplicar correcoes ou novas features, a recomendacao e marcar o estado atual como uma baseline estavel:

```bash
git tag -a v0.1.0 -m "Baseline funcional inicial"
git push origin v0.1.0
```

Essa tag marca o codigo funcional atual. A documentacao nova pode ser versionada depois, em commit separado.
