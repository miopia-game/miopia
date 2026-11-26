"""Capture real scenes or explore observed states with seeded input macros.

This is bounded exploration, not a solver or proof that all rooms are reachable.
"""
import argparse
from collections import Counter, defaultdict
import gc
import json
import math
import os
from pathlib import Path
import random
import statistics
import sys
import tempfile
import time
import traceback
import tracemalloc
from visual_probe import analyze_surface


def snapshot(app):
    j = app.jogo
    if j is None:
        return {'app': app.estado}
    l = j.lume
    return {'app': app.estado, 'jornada': j.estado, 'biome': j.etapa,
            'vertical': bool(j.em_vertical), 'position': [round(float(x), 3) for x in l.rect],
            'life': round(l.vida, 4), 'glow': round(l.energia, 4),
            'flags': sorted(j.flags), 'enemies': len(j.inimigos),
            'projectiles': sum(len(e.projeteis) for e in j.inimigos),
            'lights': len(j.vestigios)}


def node_key(state):
    position = state.get('position', [0, 0])
    return json.dumps([state['app'], state.get('jornada'), state.get('biome'),
                       state.get('vertical'), int(position[0]//160), int(position[1]//160),
                       state.get('flags', [])], ensure_ascii=False, separators=(',', ':'))


def invariant_issues(app, world_width):
    if app.jogo is None:
        return []
    j, l = app.jogo, app.jogo.lume
    issues = []
    if not all(math.isfinite(float(v)) for v in (*l.rect, l.vx, l.vy, l.vida, l.energia)):
        issues.append('non_finite_actor_state')
    if not (0 <= l.vida <= 100 and 0 <= l.energia <= 100):
        issues.append('resource_out_of_contract')
    width = world_width if j.em_vertical else j.fase.width
    if not (-.01 <= l.rect.left <= width-l.rect.w+.01):
        issues.append('horizontal_world_bounds')
    if j.estado == 'jogando' and l.rect.top > j.altura_mundo+28:
        issues.append('vertical_world_bounds')
    return issues


def run(args):
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    sys.dont_write_bytecode = True
    repo, out = args.repo.resolve(), args.out.resolve()
    if not (repo/'src/main.py').is_file():
        raise ValueError('Expected Miopia repository root')
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(repo))
    import pygame
    from src.main import App
    from src.ensaios import ENSAIOS
    from src.corte_vertical import LARGURA
    report = {'mode': args.mode, 'seed': args.seed, 'repo': str(repo), 'failures': [],
              'coverage_claim': 'observed states only; no full-map or human-playability claim',
              'profile': 'in-memory database plus disposable MIOPIA_DADOS', 'captures': []}
    state, app, last_frame = {}, None, -1
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='miopia-studio-probe-') as profile:
        previous_profile = os.environ.get('MIOPIA_DADOS')
        os.environ['MIOPIA_DADOS'] = profile
        try:
            app = App(temporaria=True)
            pygame.event.get()  # Only creation/focus events, before the tested sequence.
            held = defaultdict(bool)

            def tick(keys=(), dt=1/60):
                desired = set(keys)
                for key in [k for k, value in held.items() if value and k not in desired]:
                    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=key))
                for key in desired:
                    if not held[key]: pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
                events = []
                for event in pygame.event.get():
                    if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                        held[event.key] = event.type == pygame.KEYDOWN
                        events.append([event.type, event.key])
                    if event.type == pygame.WINDOWFOCUSLOST:
                        held.clear()
                    app.evento(event)
                app.atualizar(dt, presso=held)
                return events

            def capture(name):
                app.desenhar()
                frame = app.tela.copy()
                path = out/f'{name}.png'
                pygame.image.save(frame, str(path))
                report['captures'].append({'file': path.name, 'state': snapshot(app),
                                           'metrics': analyze_surface(frame)})

            indices = [i for i, scene in enumerate(ENSAIOS) if args.scene is None or scene.nome == args.scene]
            if args.scene is not None and not indices:
                raise ValueError(f'Unknown scene: {args.scene}. Valid scenes: {[e.nome for e in ENSAIOS]}')
            if args.mode == 'captures':
                capture('menu')
                for index in indices:
                    app.comecar_ensaio(index)
                    for _ in range(3): tick()
                    capture(f'ensaio_{index:02d}')
                report['entry'] = 'prepared scenes from the real Campo de testes; not natural campaign clears'
            else:
                if args.scene:
                    app.comecar_ensaio(indices[0])
                    report['entry'] = f'prepared scene: {args.scene}'
                else:
                    app.iniciar('historia'); app.jogar()
                    report['entry'] = 'prepared campaign start via public App API; subsequent actions use real events'
                capture('inicio')
                rng = random.Random(args.seed)
                # A held macro lasts 18 frames; a release frame separates repeated taps.
                keys = pygame
                actions = [(), (keys.K_a,), (keys.K_d,), (keys.K_a,keys.K_SPACE),
                           (keys.K_d,keys.K_SPACE), (keys.K_SPACE,), (keys.K_s,keys.K_SPACE),
                           (keys.K_d,keys.K_LSHIFT), (keys.K_a,keys.K_LSHIFT),
                           (keys.K_j,), (keys.K_l,), (keys.K_k,), (keys.K_e,),
                           (keys.K_d,keys.K_j), (keys.K_a,keys.K_j),
                           (keys.K_s,keys.K_j), (keys.K_LCTRL,keys.K_j)]
                visits, attempts, edges = Counter(), Counter(), Counter()
                state = snapshot(app); previous_node = node_key(state)
                nodes = {previous_node: state}; visits[previous_node] += 1
                durations, action, overlaps, restarts = [], (), 0, 0
                gc.collect(); tracemalloc.start(); retained_start = tracemalloc.get_traced_memory()[0]
                trace = (out/'trace.jsonl').open('w', encoding='utf-8')
                try:
                    for n in range(args.frames):
                        last_frame = n
                        if n % 19 == 0:
                            current_node = node_key(snapshot(app))
                            weights = [1/(1+attempts[(current_node, i)]) for i in range(len(actions))]
                            choice = rng.choices(range(len(actions)), weights=weights)[0]
                            attempts[(current_node, choice)] += 1
                            action = actions[choice]
                        chosen = () if n % 19 == 18 else action
                        if app.estado in ('pausa', 'mapa'): chosen = (keys.K_ESCAPE,) if n % 2 == 0 else ()
                        elif app.estado in ('morte', 'prologo', 'capitulo') or (app.jogo and app.jogo.dialogo):
                            chosen = (keys.K_RETURN,) if n % 2 == 0 else ()
                        elif app.estado == 'fim': break
                        elif app.jogo is None:
                            app.iniciar('historia'); app.jogar(); restarts += 1
                        dt = (.001 if args.extreme else 1/120) if n % 97 == 0 else .15 if n % 71 == 0 else .05 if n % 53 == 0 else 1/60
                        t0 = time.perf_counter(); events = tick(chosen, dt); durations.append(time.perf_counter()-t0)
                        state = snapshot(app); current_node = node_key(state)
                        nodes.setdefault(current_node, state); visits[current_node] += 1
                        edges[(previous_node, current_node)] += 1; previous_node = current_node
                        issues = invariant_issues(app, LARGURA)
                        if app.jogo and app.jogo.estado == 'jogando' and not app.jogo.lume.em_corda and app.jogo.destino_vertical is None:
                            body = app.jogo.lume.rect
                            collides = any(not p.atravessavel and body.clip(p.rect).w > .5 and body.clip(p.rect).h > .5 for p in app.jogo.solidos)
                            overlaps = overlaps+1 if collides else 0
                            if overlaps > 10: issues.append('persistent_solid_overlap_candidate')
                        else: overlaps = 0
                        record = {'frame': n, 'requested_dt': dt, 'events': events, 'state': state, 'issues': issues}
                        trace.write(json.dumps(record, ensure_ascii=False)+'\n')
                        if n % args.capture_every == 0: capture(f'frame_{n:05d}')
                        if issues:
                            report['failures'].append(record); capture('falha'); break
                    gc.collect(); retained_end, peak = tracemalloc.get_traced_memory()
                    ordered = sorted(durations)
                    report.update(frames_executed=len(durations), unique_observed_nodes=len(nodes),
                                  transitions=sum(edges.values()), restarts=restarts,
                                  python_memory_retained_delta=retained_end-retained_start,
                                  python_memory_peak=peak,
                                  memory_scope='tracemalloc includes the explorer graph and telemetry; not total RSS or proof of a game leak',
                                  update_seconds_median=statistics.median(ordered) if ordered else None,
                                  update_seconds_p95=ordered[min(len(ordered)-1, int(.95*len(ordered)))] if ordered else None,
                                  timing_scope='headless Python update time with tracing; not actual display FPS/latency or total RSS')
                    graph = {'nodes': [{'id': key, 'visits': visits[key], 'state': value} for key, value in nodes.items()],
                             'edges': [{'from': a, 'to': b, 'count': count} for (a,b),count in edges.items()]}
                    (out/'state_graph.json').write_text(json.dumps(graph, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
                finally:
                    trace.close(); tracemalloc.stop()
                capture('final')
        except Exception as exc:
            report['failures'].append({'frame': last_frame, 'state': state, 'exception': repr(exc),
                                       'traceback': traceback.format_exc()})
        finally:
            if app is not None: app.mem.db.close()
            pygame.quit()
            if previous_profile is None: os.environ.pop('MIOPIA_DADOS', None)
            else: os.environ['MIOPIA_DADOS'] = previous_profile
    report['seconds'] = round(time.perf_counter()-started, 3)
    (out/'probe_result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('captures',)}, ensure_ascii=False, indent=2))
    return 1 if report['failures'] else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--mode', choices=['captures', 'explore'], default='captures')
    parser.add_argument('--scene', help='Exact Campo de testes name; omitted captures all scenes or explores campaign start')
    parser.add_argument('--frames', type=int, default=3000)
    parser.add_argument('--seed', type=int, default=9101)
    parser.add_argument('--capture-every', type=int, default=300)
    parser.add_argument('--extreme', action='store_true', help='Include requested dt=.001 as diagnostic stress')
    args = parser.parse_args()
    if args.frames <= 0 or args.capture_every <= 0:
        parser.error('frames and capture-every must be positive')
    return run(args)


if __name__ == '__main__':
    raise SystemExit(main())
