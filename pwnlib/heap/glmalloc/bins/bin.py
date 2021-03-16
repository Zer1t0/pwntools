from pwnlib.heap.glmalloc.basic_formatter import BasicFormatter


class Bins(object):
    """Base class to be inherit by the bins sequences. This class provides
    the methods to access the bins array as well as standard implementation
    of the __str__ method.
    """

    def __init__(self, bins):
        self._bins = bins
        self._basic_formatter = BasicFormatter()

    @property
    def bins(self):
        """(:obj:`list` of :class:`Bin`): The bins of the sequence."""
        return self._bins

    def __getitem__(self, item):
        return self._bins[item]

    def __len__(self):
        return len(self._bins)

    def __iter__(self):
        return iter(self._bins)

    def __str__(self):
        msg = [
            self._basic_formatter.header(self._name()),
            self._format_bins(self._start_index()),
            self._basic_formatter.footer()
        ]
        return "\n".join(msg)

    def _name(self):
        return self.__class__.__name__

    def _start_index(self):
        return 0

    def _format_bins(self, start_index=0):
        bins_str = []
        for i, bin_ in enumerate(self.bins):
            if len(bin_) > 0:
                bins_str.append("[{}] {}".format(
                    i + start_index, bin_)
                )

        if bins_str:
            return "\n".join(bins_str)
        else:
            return "    [-] No chunks found"

    def summary(self, start_index=0):
        bins_str = []
        for i, bin_ in enumerate(self.bins):
            if len(bin_) > 0:
                bins_str.append(
                    "    [{}] {:#x} ({})".format(
                        start_index + i, bin_.chunks_size, len(bin_))
                )

        if bins_str:
            return "\n".join(bins_str)
        else:
            return "    [-] No chunks found"


class Bin(object):
    """Base class to be inherit by the bins. This class provides the basic info
    of the bin entry as well as the chunks of the bin.
    """

    def __init__(self, bin_entry, malloc_chunks, safe_link=False):
        self._bin_entry = bin_entry
        self._malloc_chunks = malloc_chunks
        self._safe_link = safe_link

    @property
    def bin_entry(self):
        """:class:`BinEntry`: The entry of malloc_state or
            tcache_perthread_struct for the bin."""
        return self._bin_entry

    @property
    def fd(self):
        """:class:`int`: Shortcut to the fd pointer of the entry of the current bin."""
        return self.bin_entry.fd

    @property
    def bk(self):
        """:class:`int`: Shortcut to the bk pointer of the entry of the current bin."""
        return self.bin_entry.bk

    @property
    def chunks_size(self):
        """:class:`int`: Size which should have the chunks in the bin."""
        return self.bin_entry.chunks_size

    @property
    def malloc_chunks(self):
        """:obj:`list` of :class:`MallocChunk`: The chunks which are
            inserted in the bin."""
        return self._malloc_chunks

    @property
    def chunks(self):
        """:obj:`list` of :class:`MallocChunk`: Alias for malloc_chunks."""
        return self.malloc_chunks

    def __len__(self):
        return len(self.malloc_chunks)

    def __iter__(self):
        return iter(self.malloc_chunks)

    def __str__(self):
        msg = [self._name()]

        if self.chunks_size != 0:
            msg.append(" {:#x}".format(self.chunks_size))

        msg.append(" ({})".format(len(self.malloc_chunks)))

        next_address = self.fd
        for chunk in self.malloc_chunks:
            flags = chunk.format_flags_as_str()
            msg.append(
                " => Chunk({:#x} {:#x}".format(next_address, chunk.size)
            )
            if flags:
                msg.append(" {}".format(flags))
            msg.append(")")

            if self._safe_link:
                next_address = chunk.fd_demangled
            else:
                next_address = chunk.fd

        msg.append(" => {:#x}".format(next_address))
        return "".join(msg)

    def _name(self):
        return self.__class__.__name__


class BinEntry(object):
    """Class to contain the common information of each bin entry.
    """

    def __init__(self, address, fd, bk=0, chunks_size=0):
        #: :class:`int`: The address of the bin entry.
        self.address = address

        #: :class:`int`: The address of first chunk of the bin.
        self.fd = fd

        #: :class:`int`: The address of last chunk of the bin. 0 if not used.
        self.bk = bk

        #: :class:`int`: Size which should have the chunks in the bin. 0 if
        #: not used.
        self.chunks_size = chunks_size
