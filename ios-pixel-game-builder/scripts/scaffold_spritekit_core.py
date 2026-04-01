#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SwiftFile:
    relpath: str
    content: str


CORE_FILES: list[SwiftFile] = [
    SwiftFile(
        relpath="CodexPixelCore/GameScene.swift",
        content="""import SpriteKit

final class GameScene: SKScene {
    private let cameraNode = SKCameraNode()
    private let player = SKSpriteNode(color: .white, size: CGSize(width: 16, height: 16))
    private var input = InputState()

    override func didMove(to view: SKView) {
        // Pixel-friendly default (avoid blur)
        SKTexture.defaultFilteringMode = .nearest

        backgroundColor = .black

        camera = cameraNode
        addChild(cameraNode)

        player.position = .zero
        addChild(player)

        // TODO: Replace with your pixel-perfect scaling strategy (see references/pixel-rendering-spritekit.md)
    }

    override func update(_ currentTime: TimeInterval) {
        let speed: CGFloat = 120
        let v = input.moveVector
        player.position.x += v.dx * speed * (1.0 / 60.0)
        player.position.y += v.dy * speed * (1.0 / 60.0)

        // Simple camera follow
        cameraNode.position = player.position
    }

    // MARK: - Touch input (MVP)

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        input.updateTouches(touches, in: self)
    }

    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        input.updateTouches(touches, in: self)
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        input.endTouches(touches)
    }
}
""",
    ),
    SwiftFile(
        relpath="CodexPixelCore/InputState.swift",
        content="""import SpriteKit

struct InputVector {
    var dx: CGFloat = 0
    var dy: CGFloat = 0
}

final class InputState {
    private(set) var moveVector = InputVector()
    private var primaryTouch: UITouch?
    private var origin: CGPoint = .zero

    func updateTouches(_ touches: Set<UITouch>, in node: SKNode) {
        // MVP: one-finger joystick anywhere on screen
        if primaryTouch == nil {
            primaryTouch = touches.first
            if let t = primaryTouch {
                origin = t.location(in: node)
            }
        }
        guard let t = primaryTouch else { return }
        let p = t.location(in: node)
        let dx = p.x - origin.x
        let dy = p.y - origin.y

        // Deadzone + clamp
        let deadzone: CGFloat = 8
        let maxRadius: CGFloat = 48
        let len = sqrt(dx*dx + dy*dy)
        if len < deadzone {
            moveVector = InputVector(dx: 0, dy: 0)
            return
        }
        let scale = min(1, maxRadius / max(len, 0.0001))
        moveVector = InputVector(dx: dx * scale / maxRadius, dy: dy * scale / maxRadius)
    }

    func endTouches(_ touches: Set<UITouch>) {
        if let t = primaryTouch, touches.contains(t) {
            primaryTouch = nil
            moveVector = InputVector(dx: 0, dy: 0)
        }
    }
}
""",
    ),
]


def _write_file(root: Path, f: SwiftFile) -> None:
    path = root / f.relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f.content, encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Scaffold minimal SpriteKit core Swift files for a pixel-art iOS game.",
    )
    p.add_argument("--out", default=".", help="Output directory (default: current directory)")
    args = p.parse_args()

    out = Path(os.path.expanduser(args.out)).resolve()
    for f in CORE_FILES:
        _write_file(out, f)
    print(f"[OK] Wrote {len(CORE_FILES)} files under: {out}/CodexPixelCore")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

