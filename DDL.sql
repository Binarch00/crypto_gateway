
--
-- Table structure for table `address_outputs`
--

CREATE TABLE `address_outputs` (
  `id` int(11) NOT NULL,
  `block` int(10) UNSIGNED NOT NULL,
  `address` varchar(100) NOT NULL,
  `value` decimal(16,8) NOT NULL,
  `block_hash` VARCHAR(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `address_outputs`
--
ALTER TABLE `address_outputs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `block` (`block`),
  ADD KEY `address` (`address`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `address_outputs`
--
ALTER TABLE `address_outputs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;


-- --------------------------------------------------------

--
-- Table structure for table `ipn`
--

CREATE TABLE `ipn` (
  `id` int(11) NOT NULL,
  `address` varchar(100) NOT NULL,
  `type` varchar(10) NOT NULL DEFAULT 'btc',
  `max_confirms` int(11) NOT NULL DEFAULT '3',
  `url` text NOT NULL,
  `status` enum('new','ready','done','fail') NOT NULL DEFAULT 'new',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ipn`
--
ALTER TABLE `ipn`
  ADD PRIMARY KEY (`id`),
  ADD KEY `address` (`address`),
  ADD KEY `status` (`status`),
  ADD KEY `created_at` (`created_at`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ipn`
--
ALTER TABLE `ipn`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;


ALTER TABLE `ipn` ADD UNIQUE `unique_index`(`address`, `type`, `url`(100));


-- --------------------------------------------------------

--
-- Table structure for table `settings`
--

CREATE TABLE `settings` (
  `name` varchar(150) NOT NULL,
  `value` text NOT NULL,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `settings`
--

INSERT INTO `settings` (`name`, `value`, `updated_at`) VALUES
('ipn_sync_block', '0', '2020-03-27 00:03:04');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `settings`
--
ALTER TABLE `settings`
  ADD PRIMARY KEY (`name`);