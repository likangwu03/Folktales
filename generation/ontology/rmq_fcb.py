import math

class RMQ_FCB:
    """    
    RMQ con Farach-Colton–Bender para arreglos con diferencias arbitrarias.
    Implementación estándar con división en bloques y pre-cómputo por máscara.
    Pre: arr (lista) de valores (típicamente profundidades del Euler tour).
    build -> O(n)
    query(l, r) -> devuelve el índice del mínimo en arr entre l..r (inclusive) en O(1).
    """

    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)
        if self.n == 0:
            return

        # Tamaño de bloque b = max(1, floor(log2(n) / 2))
        self.b = max(1, (math.floor(math.log2(self.n)) // 2) or 1)
        self.nb = (self.n + self.b - 1) // self.b  # número de bloques

        # Índices globales del mínimo de cada bloque
        self.block_min_idx = [0] * self.nb

        # Máscaras por bloque: para cada bloque representamos la secuencia de comparaciones
        # entre elementos adyacentes (arr[i+1] >= arr[i] -> bit 1; arr[i+1] < arr[i] -> bit 0).
        self.masks = [0] * self.nb

        # Tablas precomputadas por cada máscara encontrada:
        # mask -> tabla (b x b) tal que table[i][j] = offset del mínimo en i..j dentro del bloque.
        self.mask_tables = {}

        # Construir mínimos de bloque, máscaras y tablas
        self._prepare_blocks()

        # Construir sparse table sobre los mínimos de bloque
        self._build_block_sparse_table()

    def _prepare_blocks(self):
        n, b = self.n, self.b
        for block in range(self.nb):
            start = block * b
            end = min(n, start + b)

            # Calcular índice global del mínimo dentro del bloque
            min_idx = start
            for i in range(start + 1, end):
                if self.arr[i] < self.arr[min_idx]:
                    min_idx = i
            self.block_min_idx[block] = min_idx

            # Construir máscara del bloque:
            # longitud = end - start
            # bit j = 1 si arr[start+j+1] >= arr[start+j], de lo contrario 0.
            mask = 0
            for j in range(start, end - 1):
                mask = (mask << 1) | (1 if self.arr[j+1] >= self.arr[j] else 0)

            self.masks[block] = (mask, end - start)

            # Crear tabla solo si la máscara aún no fue registrada
            if mask not in self.mask_tables:
                length = end - start
                self.mask_tables[mask] = self._build_mask_table(mask, length)

    def _build_mask_table(self, mask, length):
        """
        Dada una máscara (patrón de comparaciones) y la longitud del bloque,
        construir la tabla RMQ relativa para ese patrón:
        Para offsets i..j (0 <= i <= j < length),
        table[i][j] = offset del mínimo dentro del subrango i..j.

        Observación: el mínimo relativo solo depende del patrón de comparaciones,
        no de los valores absolutos.
        """

        # Reconstruimos un arreglo relativo partiendo de 0 y aplicando +1 o -1
        # según los bits de la máscara.
        vals = [0] * length

        # Extraemos los bits de la máscara en una lista, ordenados de izquierda a derecha.
        bits = []
        for k in range(length - 1):
            # El bit que representa la comparación k está en la posición (length - 2 - k)
            bitpos = (length - 2 - k)
            bit = (mask >> bitpos) & 1 if bitpos >= 0 else 0
            bits.append(bit)

        # Construcción del arreglo relativo
        for i in range(1, length):
            vals[i] = vals[i-1] + (1 if bits[i-1] == 1 else -1)

        # Construimos la tabla RMQ local: table[i][j] = offset del mínimo en vals[i..j]
        table = [[0] * length for _ in range(length)]
        for i in range(length):
            min_pos = i
            min_val = vals[i]
            table[i][i] = 0
            for j in range(i + 1, length):
                if vals[j] < min_val:
                    min_val = vals[j]
                    min_pos = j
                table[i][j] = min_pos - i

        return table

    def _build_block_sparse_table(self):
        # Construimos una sparse table sobre los mínimos de bloque
        self.block_depths = [self.arr[self.block_min_idx[i]] for i in range(self.nb)]
        m = self.nb

        if m == 0:
            self.bs_log = []
            self.bs_st = []
            return

        # Precomputar logaritmos
        self.bs_log = [0] * (m + 1)
        for i in range(2, m + 1):
            self.bs_log[i] = self.bs_log[i // 2] + 1

        K = self.bs_log[m] + 1

        # bs_st[k][i] = índice de bloque con el mínimo en el rango de bloques i..i+2^k-1
        self.bs_st = [[0] * m for _ in range(K)]
        for i in range(m):
            self.bs_st[0][i] = i

        k = 1
        while (1 << k) <= m:
            length = 1 << k
            half = 1 << (k - 1)
            for i in range(0, m - length + 1):
                left = self.bs_st[k - 1][i]
                right = self.bs_st[k - 1][i + half]
                self.bs_st[k][i] = left if self.block_depths[left] <= self.block_depths[right] else right
            k += 1

    def _block_rmq(self, Lb, Rb):
        """Devuelve el índice de bloque con mínimo entre Lb..Rb (inclusive)."""
        if Lb > Rb:
            return None
        if Lb == Rb:
            return Lb
        k = self.bs_log[Rb - Lb + 1]
        left = self.bs_st[k][Lb]
        right = self.bs_st[k][Rb - (1 << k) + 1]
        return left if self.block_depths[left] <= self.block_depths[right] else right

    def query(self, L, R):
        """
        Devuelve el índice global del mínimo en arr entre L..R (inclusive).
        """
        if L > R:
            L, R = R, L
        if L < 0 or R >= self.n:
            raise IndexError("query indices out of range")

        b = self.b
        Lb = L // b
        Rb = R // b

        # Caso: ambos índices en el mismo bloque → usar tabla interna
        if Lb == Rb:
            mask, length = self.masks[Lb]
            t = self.mask_tables[mask]
            off = t[L % b][R % b]   # offset dentro del bloque
            return Lb * b + (L % b) + off

        # Mínimo en el extremo izquierdo
        maskL, lenL = self.masks[Lb]
        tL = self.mask_tables[maskL]
        offL = tL[L % b][lenL - 1]
        idxL = Lb * b + (L % b) + offL

        # Mínimo en el extremo derecho
        maskR, lenR = self.masks[Rb]
        tR = self.mask_tables[maskR]
        offR = tR[0][R % b]
        idxR = Rb * b + offR

        # Mínimo en bloques intermedios, si los hay
        if Lb + 1 <= Rb - 1:
            mid_block = self._block_rmq(Lb + 1, Rb - 1)
            idxM = self.block_min_idx[mid_block]

            cand = idxL
            if self.arr[idxM] < self.arr[cand]:
                cand = idxM
            if self.arr[idxR] < self.arr[cand]:
                cand = idxR
            return cand
        else:
            # No hay bloques intermedios: comparar solo extremos
            return idxL if self.arr[idxL] <= self.arr[idxR] else idxR